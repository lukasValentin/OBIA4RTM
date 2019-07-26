#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 13:45:23 2019

@author: lukas
"""
from Py6S import PredefinedWavelengths, SixS, Wavelength, AtmosProfile, AeroProfile, Geometry
import datetime
import math
import os
import sys
import ee
from ee.ee_exception import EEException
from OBIA4RTM.S2_PreProcessor.atmospheric import Atmospheric
from OBIA4RTM.configurations.logger import get_logger, close_logger


class s2_Py6S_atcorr:
    """
    class for performing Sentinel-2 atmospheric correction of Top-of-Atmosphere
    imagery to Surface Reflectance values using the 6S algorithm.
    Code written by Sam Murphy (https://github.com/samsammurphy) and made
    availabe via Apache License 2.0 on Github
    (https://github.com/samsammurphy/gee-atmcorr-S2).
    Slightly modified by Lukas Graf for usage in OBIA4RTM
    """
    def __init__(self):
        """
        class constructor and basic setup of processing environment
        """
        sys.path.append(os.path.join(os.path.dirname(os.getcwd()),'bin'))
        # get a logger for recording sucess and error messages
        self.__logger = get_logger()
        self.__logger.info('Setting up Google EE environment for Sentinel-2 '\
                           'atmospheric correction using the 6S algorithm')
        try:
            ee.Initialize()
        except EEException:
            self.__logger.error('No (valid) Earth-Engine credentials provided!',
                                exc_info=True)
            close_logger(self.__logger)
            sys.exit(-1)
        # for storing the metadata
        self.info = None
        # for the image object
        self.__S2 = None
        # for the solar zenith angle and the scene timestamp
        self.__solar_z = None
        self.__scene_date = None


    @staticmethod
    def spectralResponseFunction(bandname):
        """
        Extract spectral response function for given band name
        Modification of the original source code:
        only those bands are available that are used in OBIA4RTM

        Parameters
        ----------
        bandname : String
            Name of the Sentinel-2 spectral band to be processed, only the
            nine Sentinel-2 bands used in OBIA4RTM are processed

        Returns
        -------
        Wavelength : Tuple
            wavelengths of the desired Sentinel-2 band (required for 6S to run)
        """
        bandSelect = {
            'B1':PredefinedWavelengths.S2A_MSI_01,
            'B2':PredefinedWavelengths.S2A_MSI_02,
            'B3':PredefinedWavelengths.S2A_MSI_03,
            'B4':PredefinedWavelengths.S2A_MSI_04,
            'B5':PredefinedWavelengths.S2A_MSI_05,
            'B6':PredefinedWavelengths.S2A_MSI_06,
            'B7':PredefinedWavelengths.S2A_MSI_07,
            'B8A':PredefinedWavelengths.S2A_MSI_09,
            'B11':PredefinedWavelengths.S2A_MSI_12,
            'B12':PredefinedWavelengths.S2A_MSI_13,
            }
        return Wavelength(bandSelect[bandname])


    def toa_to_rad(self, bandname):
        """
        Converts top of atmosphere reflectance to at-sensor radiance

        Parameters
        ----------
        bandname : String
            name of the Sentinel-2 spectral band to be processed, only the
            nine Sentinel-2 bands used in OBIA4RTM are processed
        info : Dictionary
            metadata available form GEE image

        Returns
        -------
        rad : ee.image.Image
            At sensor Radiance
        """
        # solar exoatmospheric spectral irradiance
        ESUN = self.info['SOLAR_IRRADIANCE_'+bandname]
        solar_z = self.info['MEAN_SOLAR_ZENITH_ANGLE']
        solar_angle_correction = math.cos(math.radians(solar_z))
        # Earth-Sun distance (from day of year)
        doy = self.__scene_date.timetuple().tm_yday
        # http://physics.stackexchange.com/questions/177949/earth-sun-distance-on-a-given-day-of-the-year
        d = 1 - 0.01672 * math.cos(0.9856 * (doy-4))
        # conversion factor
        multiplier = ESUN*solar_angle_correction/(math.pi*d**2)
        # top of atmosphere reflectance
        toa = self.__S2.divide(10000)
        # at-sensor radiance
        rad = toa.select(bandname).multiply(multiplier)
        return rad


    def surface_reflectance(self, s, bandname):
        """
        Calculate surface reflectance from at-sensor radiance given waveband name
        using the 6S algorithm

        Parameters
        ----------
        s : Six6 object
            object of Py6S class
        bandname : String
            name of the Sentinel-2 spectral band to be processed, only the
            nine Sentinel-2 bands used in OBIA4RTM are processed

        Returns
        -------
        ref : ee.image.Image
            surface reflectance
        """
        # run 6S for this waveband
        s.wavelength = self.spectralResponseFunction(bandname)
        s.run()
        # extract 6S outputs
        Edir = s.outputs.direct_solar_irradiance             #direct solar irradiance
        Edif = s.outputs.diffuse_solar_irradiance            #diffuse solar irradiance
        Lp   = s.outputs.atmospheric_intrinsic_radiance      #path radiance
        absorb  = s.outputs.trans['global_gas'].upward       #absorption transmissivity
        scatter = s.outputs.trans['total_scattering'].upward #scattering transmissivity
        tau2 = absorb * scatter                              #total transmissivity
        # radiance to surface reflectance
        rad = self.toa_to_rad(bandname)
        ref = rad.subtract(Lp).multiply(math.pi).divide(tau2*(Edir+Edif))
        return ref


    def run_py6s(self, geom, acqui_date):
        """
        runs the 6S algorithm for atmospheric correction on a user-defined
        geometry and date on Sentinel-2 imagery
        Requires Google Earth-Engine Python API client

        Parameters
        ----------
        geom : EE-Geometry
            Google EE geometry specify the geographic extent to be processed
        acqui_date : String
            date (YYYY-MM-dd) of the desired scene to be processed

        Returns
        -------
        s2_surf : ee.image.Image
            Google EE image instance with surface reflectance values
        """
        date = ee.Date(acqui_date)
        # get the Sentinel-2 image at or immediately after the specified date
        self.__S2 = ee.Image(
                ee.ImageCollection('COPERNICUS/S2')
                .filterBounds(geom)
                .filterDate(date,date.advance(3,'month'))
                .sort('system:time_start')
                .first()
                )
        # extract the relevant metadata for carrying out the atmospheric correction
        self.info = self.__S2.getInfo()['properties']
        # get the solar zenith angle an the scene data
        self.__scene_date = datetime.datetime.utcfromtimestamp(
                    self.info['system:time_start']/1000)
        self.__solar_z = self.info['MEAN_SOLAR_ZENITH_ANGLE']
        # log the identifier of the processed scene
        scene_id = self.info.get('DATASTRIP_ID')
        self.__logger.info("Starting Processing scene '{}' using GEE and Py6S".format(
                scene_id))
        # get the atmospheric constituents
        # i.e water vapor (h2o), ozone (o3), aerosol optical thickness (aot)
        h2o = Atmospheric.water(geom, date).getInfo()
        o3 = Atmospheric.ozone(geom, date).getInfo()
        aot = Atmospheric.aerosol(geom, date).getInfo()
        # get the average altitude of the region to be processed
        # for the Digital Elevation Model (DEM) the Shuttle Radar Topography
        # Mission (SRTM) is used (Version 4) as it covers most parts of the
        # Earth
        SRTM = ee.Image('CGIAR/SRTM90_V4')
        alt = SRTM.reduceRegion(reducer = ee.Reducer.mean(),
                                geometry = geom.centroid()).get('elevation').getInfo()
        message = "Atcorr-Metadata: Water-Vapor = {0}, Ozone = {1}, AOT = {2}, "\
                    " Average Altitude (m) = {3}".format(
                            h2o, o3, aot, alt)
        self.__logger.info(message)
        # Py6S uses units of kilometers
        km = alt/1000
        # create a 6S object from the Py6S class
        # Instantiate
        s = SixS()
        # Atmospheric constituents
        s.atmos_profile = AtmosProfile.UserWaterAndOzone(h2o,o3)
        s.aero_profile = AeroProfile.Continental
        s.aot550 = aot
        # Earth-Sun-satellite geometry
        s.geometry = Geometry.User()
        s.geometry.view_z = 0                       # always NADIR (simplification!)
        s.geometry.solar_z = self.__solar_z         # solar zenith angle
        s.geometry.month = self.__scene_date.month  # month and day used for Earth-Sun distance
        s.geometry.day = self.__scene_date.day      # month and day used for Earth-Sun distance
        s.altitudes.set_sensor_satellite_level()
        s.altitudes.set_target_custom_altitude(km)
        self.__logger.info('Atcorr: Starting processing of Sentinel-2 scene!')
        # now iterate over the nine relevant Sentinel-2 bands to perform the
        # atmospheric correction and get the surface reflectance
        # go through the spectral bands
        B1_surf = self.surface_reflectance(s, 'B1')
        B2_surf = self.surface_reflectance(s, 'B2')
        B3_surf = self.surface_reflectance(s, 'B3')
        B4_surf = self.surface_reflectance(s, 'B4')
        B5_surf = self.surface_reflectance(s, 'B5')
        B6_surf = self.surface_reflectance(s, 'B6')
        B7_surf = self.surface_reflectance(s, 'B7')
        B8A_surf = self.surface_reflectance(s, 'B8A')
        B11_surf = self.surface_reflectance(s, 'B11')
        B12_surf = self.surface_reflectance(s, 'B12')
        self.__logger.info('Atcorr: Finished processing of Sentinel-2 scene!')
        # make a stack of the spectral bands
        S2_surf = B1_surf.addBands(B2_surf).addBands(B3_surf).addBands(B4_surf).addBands(B5_surf).addBands(B6_surf).addBands(B7_surf).addBands(B8A_surf).addBands(B11_surf).addBands(B12_surf)
        # return the surface reflectance image
        return S2_surf
