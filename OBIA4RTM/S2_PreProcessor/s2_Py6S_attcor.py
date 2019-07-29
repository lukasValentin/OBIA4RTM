#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 13:45:23 2019

This module is part of OBIA4RTM with code taken from
https://github.com/samsammurphy/gee-atmcorr-S2 available under Apache 2.0 licence
This module contains a class that is mainly a object-oriented version of the
jupyter notebook available in the repository outlined above. Some modifactions
were made to fit the requirements of OBIA4RTM.

NOTE: This module makes use of Google Earth Engine.
For setting up the Python Client API please see:
    https://developers.google.com/earth-engine/python_install

Copyright (c) Sam Murphy (https://github.com/samsammurphy)

Slight changes from the original source code were made (class structure);
functionalities themselves have not been altered

Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "{}"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright {yyyy} {name of copyright owner}

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
from Py6S import PredefinedWavelengths, SixS, Wavelength, AtmosProfile, AeroProfile, Geometry, OutputParsingError
import datetime
import math
import os
import sys
import ee
from ee.ee_exception import EEException
import OBIA4RTM
from OBIA4RTM.S2_PreProcessor.atmospheric import Atmospheric
from OBIA4RTM.S2_PreProcessor.cloud_masking import mask_clouds
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
        # find the directory the 6S binary has been installed to
        # this is a sub-directory of the OBIA4RTM_HOME
        with open(os.path.dirname(OBIA4RTM.__file__) + os.sep + 'OBIA4RTM_HOME',
                  'r') as data:
            obia4rtm_dir = data.readline()
        self.sixS_install_dir = obia4rtm_dir + os.sep + 'sixS'+  os.sep + 'src' + os.sep + '6SV1.1'
        # make sure that 6S is installed
        if not os.path.isdir(self.sixS_install_dir):
            print("Error: 6S is not installed on your computer or cannot be found!\n"\
                  "Expected installation location: '{}'\n"\
                  "You might want to run OBIA4RTM.S2_PreProcessor.install_6S "\
                  "for installing 6S".format(self.sixS_install_dir))
        # add this directory of 6S binary to system path temporally (does not work properly)
        # sys.path.append(sixS_install_dir)
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
        self.S2 = None
        # for the solar zenith angle and the scene timestamp
        self.solar_z = None
        self.scene_date = None


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
        doy = self.scene_date.timetuple().tm_yday
        # http://physics.stackexchange.com/questions/177949/earth-sun-distance-on-a-given-day-of-the-year
        d = 1 - 0.01672 * math.cos(0.9856 * (doy-4))
        # conversion factor
        multiplier = ESUN*solar_angle_correction/(math.pi*d**2)
        # at-sensor radiance
        rad = self.S2.select(bandname).multiply(multiplier)
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
        try:
            s.run()
            # extract 6S outputs
            Edir = s.outputs.direct_solar_irradiance             #direct solar irradiance
            Edif = s.outputs.diffuse_solar_irradiance            #diffuse solar irradiance
            Lp   = s.outputs.atmospheric_intrinsic_radiance      #path radiance
            absorb  = s.outputs.trans['global_gas'].upward       #absorption transmissivity
            scatter = s.outputs.trans['total_scattering'].upward #scattering transmissivity
            tau2 = absorb * scatter                              #total transmissivity
        except OutputParsingError:
            self.__logger.error('Failed to read 6S outputs!',
                                exc_info=True)
            close_logger(self.__logger)
            sys.exit(-1)
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
        self.S2 = ee.Image(
                ee.ImageCollection('COPERNICUS/S2')
                .filterBounds(geom)
                .filterDate(date,date.advance(3,'month'))
                .sort('system:time_start')
                .first()
                )
        # extract the relevant metadata for carrying out the atmospheric correction
        self.info = self.S2.getInfo()['properties']
        # get the solar zenith angle an the scene data
        self.scene_date = datetime.datetime.utcfromtimestamp(
                    self.info['system:time_start']/1000)
        self.solar_z = self.info['MEAN_SOLAR_ZENITH_ANGLE']
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
        # Earth (90 arc-sec data is used)
        SRTM = ee.Image('CGIAR/SRTM90_V4')
        alt = SRTM.reduceRegion(reducer = ee.Reducer.mean(),
                                geometry = geom.centroid()).get('elevation').getInfo()
        message = "Atcorr-Metadata: Water-Vapor = {0}, Ozone = {1}, AOT = {2}, "\
                    " Average Altitude (m) = {3}".format(
                            h2o, o3, aot, alt)
        self.__logger.info(message)
        # Py6S uses units of kilometers
        km = alt/1000
        # mask out clouds and cirrus from the imagery using the cloud scor
        # algorithm provided by Sam Murhpy under Apache 2.0 licence
        # see: https://github.com/samsammurphy/cloud-masking-sentinel2/blob/master/cloud-masking-sentinel2.ipynb
        # also converts the image values to top-of-atmosphere reflectance
        self.S2 = mask_clouds(self.S2, option=1)
        # create a 6S object from the Py6S class
        # Instantiate (use the explizit path to installation directory of the
        # 6S binary as otherwise there might be an error)
        s = SixS()
        # Atmospheric constituents
        s.atmos_profile = AtmosProfile.UserWaterAndOzone(h2o,o3)
        s.aero_profile = AeroProfile.Continental
        s.aot550 = aot
        # Earth-Sun-satellite geometry
        s.geometry = Geometry.User()
        s.geometry.view_z = 0                       # always NADIR (simplification!)
        s.geometry.solar_z = self.solar_z         # solar zenith angle
        s.geometry.month = self.scene_date.month  # month and day used for Earth-Sun distance
        s.geometry.day = self.scene_date.day      # month and day used for Earth-Sun distance
        s.altitudes.set_sensor_satellite_level()
        s.altitudes.set_target_custom_altitude(km)
        self.__logger.info('6S: Starting processing of Sentinel-2 scene!')
        # now iterate over the nine relevant Sentinel-2 bands to perform the
        # atmospheric correction and get the surface reflectance
        # go through the spectral bands
        B1_surf = self.surface_reflectance(s, 'B1')
        self.__logger.info('6S: Finished processing Sentinel-2 Band 1!')
        B2_surf = self.surface_reflectance(s, 'B2')
        self.__logger.info('6S: Finished processing Sentinel-2 Band 2!')
        B3_surf = self.surface_reflectance(s, 'B3')
        self.__logger.info('6S: Finished processing Sentinel-2 Band 3!')
        B4_surf = self.surface_reflectance(s, 'B4')
        self.__logger.info('6S: Finished processing Sentinel-2 Band 4!')
        B5_surf = self.surface_reflectance(s, 'B5')
        self.__logger.info('6S: Finished processing Sentinel-2 Band 5!')
        B6_surf = self.surface_reflectance(s, 'B6')
        self.__logger.info('6S: Finished processing Sentinel-2 Band 6!')
        B7_surf = self.surface_reflectance(s, 'B7')
        self.__logger.info('6S: Finished processing Sentinel-2 Band 7!')
        B8A_surf = self.surface_reflectance(s, 'B8A')
        self.__logger.info('6S: Finished processing Sentinel-2 Band 8A!')
        B11_surf = self.surface_reflectance(s, 'B11')
        self.__logger.info('6S: Finished processing Sentinel-2 Band 11!')
        B12_surf = self.surface_reflectance(s, 'B12')
        self.__logger.info('6S: Finished processing Sentinel-2 Band 12!')
        self.__logger.info('6S: Finished processing of Sentinel-2 scene!')
        # make a stack of the spectral bands
        S2_surf = B1_surf.addBands(B2_surf).addBands(B3_surf).addBands(B4_surf).addBands(B5_surf).addBands(B6_surf).addBands(B7_surf).addBands(B8A_surf).addBands(B11_surf).addBands(B12_surf)
        # return the surface reflectance image
        close_logger(self.__logger)
        return S2_surf
