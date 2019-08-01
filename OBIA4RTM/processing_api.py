#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 08:46:00 2019

This module is part of OBIA4RTM.

Copyright (c) 2019 Lukas Graf

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

@author: Lukas Graf, graflukas@web.de
"""
import os
import sys
from configparser import ConfigParser, MissingSectionHeaderError
import OBIA4RTM
from OBIA4RTM.S2_PreProcessor.s2_Py6S_attcor import s2_Py6S_atcorr
from OBIA4RTM.S2_PreProcessor.s2_sen2core_attcor import do_sen2core_preprocessing
from OBIA4RTM.S2_PreProcessor.s2_sen2core_attcor import call_gdal_merge
from OBIA4RTM.mdata_proc.parse_s2xml import parse_s2xml
from OBIA4RTM.mdata_proc.handle_gee_metadata import parse_gee_metadata
from OBIA4RTM.mdata_proc.insert_scene_metadata import insert_scene_metadata
from OBIA4RTM.zonal_stats.get_mean_refl_ee import get_mean_refl_ee
from OBIA4RTM.zonal_stats.get_mean_refl import get_mean_refl


class API:
    """
    this is the main API wrapper class around the OBIA4RTM functionalities

    Parameters
    ----------
    use_gee : Boolean
        determines if Google Earth Engine (True) or Sen2Core (False) was /
        should be used for preprocessing and data handling
    obia4rtm_home : String
        directory that contains the config files required for OBIA4RTM.
        If None the default OBIA4RTM home dir (in the user profile) is used
    """
    def __init__(self, use_gee, obia4rtm_home=None):
        """
        class constructor
        """
        # check if use_gee is Boolean
        if type(use_gee) != bool:
            raise ValueError('Invalid value for use_gee parameter: '\
                             'Must be boolean!')
            sys.exit(-1)
        # set to class attribute
        self.__use_gee = use_gee
        # determine the OBIA4RTM user directroy where all the config files
        # are stored
        if obia4rtm_home is None:
            obia4rtm_dir = os.path.dirname(OBIA4RTM.__file__)
            fname = obia4rtm_dir + os.sep + 'OBIA4RTM_HOME'
            with open(fname, 'r') as data:
                obia4rtm_home = data.readline()
        # in any case, check if the directory is existing and can be accessed
        if not os.path.isdir(obia4rtm_home):
            raise FileNotFoundError("Your OBIA4RTM user directory seems to "\
                  "be invalid!\nPlease check your OBIA4RTM installation or the "\
                  "path you specified!")
            sys.exit(-1)
        # set the class attribute
        self.__obia4rtm_home = obia4rtm_home

        # set other class attributes to None unless specified otherwise

        # configuration files
        self.__landcover_cfg = None     # landcover configuration file
        self.__prosail_cfg = None       # prosail configuration file
        self.__soil_refl = None         # file with soil reflectance values
        # Database configuration file
        self.__backend_cgf = None      # table and schema names


    ###########################################################################
    #
    #       Public SETTER Methods
    #       only necessary if not the standard OBIA4RTM home directory
    #       (in the user profile) is used
    #
    ###########################################################################
    def set_landcover_cfgfile(self, landcover_cfg):
        """
        set landcover configuration file

        Parameters
        ----------
        landcover_cfg : String
            landcover configuration file if not the default file should be used
        """
        self.__landcover_cfg = landcover_cfg


    def set_prosail_cfgfile(self, prosail_cfg):
        """
        set landcover configuration file

        Parameters
        ----------
        prosail_cfg : String
            prosail configuration file if not the default file should be used
        """
        self.__prosail_cfg = prosail_cfg


    def set_soil_refl_file(self, soil_refl_file):
        """
        set landcover configuration file

        Parameters
        ----------
        soil_refl_file : String
            file with soil reflectance values if not the default file should
            be used
        """
        self.__soil_refl = soil_refl_file


    def set_backend_cfgfile(self, backend_cfg):
        """
        set landcover configuration file

        Parameters
        ----------
        backend_cfg : String
            backend configuration file if not the default file should be used
        """
        self.__backend_cfg = backend_cfg


    def set_tablenames(self):
        """
        sets the tablenames read from backend_cfg file into a list
        """
        if self.__backend_cfg is None:
            self.__backend_cfg = self.__obia4rtm_home + os.sep + 'obia4rtm_backend.cfg'

        parser = ConfigParser()
        try:
            parser.read(self.__backend_cfg)
        except MissingSectionHeaderError:
            raise MissingSectionHeaderError('The obia4rtm_backend.cfg does '\
                         'not fulfil the formal requirements!',
                         exc_info=True)
            sys.exit(-1)
        # get the schema name
        schema = parser.get('schema-setting', 'schema_obia4rtm')
        # read the tablenames
        table_names = []
        table_names.append(schema + "." + parser.get('schema-setting', 'table_lookuptabe'))
        table_names.append(schema + "." + parser.get('schema-setting', 'table_inv_results'))
        table_names.append(schema + "." + parser.get('schema-setting', 'table_object_spectra'))
        table_names.append(schema + "." + parser.get('schema-setting', 'table_inv_mapping'))
        self.__tablenames = table_names


    ###########################################################################
    #
    #       Public GETTER Methods
    #
    ###########################################################################
    def get_OBIA4RTM_home(self):
        """
        prints the OBIA4RTM home directory
        """
        print("The OBIA4RTM home is: '{}'".format(self.__obia4rtm_home))


    def get_use_gee(self):
        """
        prints out if Goolge Earth Engine or Sen2Core was used for
        preprocessing of the satellite imagery
        """
        if self.__use_gee:
            print('Google Earth Engine was used/ should be used for '\
                  'preprocessing of the imagery')
        else:
            print('Sen2Core was used/ shouldd be used for preprocessing of '\
                  'the imagery')
        # endif


    ###########################################################################
    #
    #       Functionality wrapper Methods (private)
    #
    ###########################################################################
    def do_gee_preprocessing(self, geom, acqui_date, option, shp_file):
        """
        method to conduct the full workflow (atcorr, cloud and
        shadow mask, zonal stats ) for imagery derived from Google Earth Engine

        Parameters
        ----------
        geom : List
            list of coordinate pairs forming a polygon that is used
            to determine the geograhic extent to be processed in GEE
        acqui_date : String
            acquisition date to be processed (format: YYYY-MM-DD)
        option : Integer
            option for cloud and shadow masking in preprocessing.
            Allowed values:     1 (ESA quality information)
                                2 (alternative algorithm)
        shp_file : String
            file path to the shape file with the object boundaries and the
            landcover / landuse information for the particular acquisition
            date
            NOTE: the shapefile must be EXACTELY in the format required
            by OBIA4RTM

        Returns
        -------
        scene_id : String
           ID of Sentinel-2 imagery
        """
        # check if GEE can be loaded
        try:
            import ee
            from ee.ee_exception import EEException
        except ModuleNotFoundError:
            print('To use Google-Earth-Engine the GEE Client Python API must '\
                  'be installed on your computer!')
            sys.exit()
        # check if the geometry is valid
        try:
            ee.Initialize()
            geom = ee.geometry.Geometry.Polygon(geom)
        except EEException:
            print('The provided geometry is not valid!')
        # create an atcorr instance
        at = s2_Py6S_atcorr()
        # run the atmospheric correction and the masking of clouds and shadows
        # this returns an ee.image.Image with surface reflectance values
        S2_SRF = at.run_py6s(geom, acqui_date, option)
        # the retrieved surface reflectance values are then processed to extract
        # per object reflectance values
        # get the tablename of the object spectra table
        if self.__tablenames is None:
            self.set_tablenames()
        tablename_obj_spec = self.__tablenames[2]
        # return the metadata as this information will be lost otherwise
        # (but is required for the inversion)
        # some formatting is necessary, however
        gee_metadata = at.info
        metadata = parse_gee_metadata(gee_metadata)
        # insert the metadata into the OBIA4RTM backend
        insert_scene_metadata(metadata, use_gee=True)
        # get the scene_id and the actual acqui date as this could differ
        # from the one specified in case on that day no scene was found
        scene_id = metadata['SCENE_ID']
        acqui_date = metadata['SENSING_TIME'][0:10] 
        # now the zonal stats function can be called
        # after that the preprocessing using GEE is finished
        get_mean_refl_ee(shp_file, S2_SRF, acqui_date, scene_id,
                         tablename_obj_spec)
        # get the SCENE_ID and return it
        return scene_id

    def do_sen2core_preprocessing(self, sentinel_data_dir,
                                   zipped, resolution, path_sen2core,
                                   shp_file, storage_dir=None):
        """
        calls the full preprocessing workflow using Sen2Core

        NOTE: Requires GDAL-Python bindings
        NOTE: Do not run this method on data already in L2 level!
            Use process_L2data instead

        Parameters
        ----------
        sentinel_data_dir : String
            path to the directory that contains the Level-1C data. In case
            the data is zipped (default when downloaded from Copernicus) specify
            the file-path of the zip
        zipped : Boolean
            specifies if the directory with the Sat data is zipped
        resolution : Integer
            spatial resolution of the atmospherically corrected imagery
            possible value: 10, 20, 60 meters
        path_sen2core : String
            directory containing Sen2Core software (top-most level; e.g.
            /home/user/Sen2Core/). Must be the same directory as specified
            during the Sen2Core installation process using the --target option
        storage_dir : String
            path to the directory the final layer stack should be moved to. If None,
            the layer stack will remain the sentinel_data_dir_l2 in the img folder

        Returns
        -------
        scene_id:
            ID of the processed Sentinel-2 scene
        
        """
        # check if input is almost L2 level -> in this case this function
        # is not suited, use process_L2data instead
        if sentinel_data_dir.find('MSIL2A') != -1:
            raise Warning('Seems as if your Sentinel data is already in Level 2A!\n'\
                          'Please use the function process_L2data from the '\
                          'processing API instead.')
            sys.exit()
        # call sen2core Python wrapper and prepare the output for usage in
        # OBIA4RTM
        # returns file name of Sentinel-2 imagery in L2 level and the
        # file path to the metadata xml
        fname_s2, metadata_xml = do_sen2core_preprocessing(sentinel_data_dir,
                                                           zipped,
                                                           resolution,
                                                           path_sen2core,
                                                           storage_dir=storage_dir)
        # get the tablename of the object spectra table
        if self.__tablenames is None:
            self.set_tablenames()
        tablename_obj_spec = self.__tablenames[2]
        # parse the metadata and insert it into the database
        metadata = parse_s2xml(metadata_xml)
        insert_scene_metadata(metadata, use_gee=False, raster=fname_s2)
        # get the scene_id and the acquisition date
        scene_id = metadata['SCENE_ID']
        acqui_date = metadata['SENSING_TIME'][0:10]
        # with that information, the zonal statistics can be computed
        # using the provided shapefile with the object boundaries and
        # the landuser/ cover information
        get_mean_refl(shp_file, fname_s2, acqui_date, scene_id,
                      tablename_obj_spec)
        # return the SCENE_ID
        return scene_id


    def process_L2data(self, sentinel_data_dir, resolution,
                       shp_file, acqui_date, storage_dir=None):
        """
        formats the output of data already acquired in ESA L2 format
        in the format required by OBIA4RTM and runs the zonal stats procedure
        to get per object reflectance values

        NOTE: Requires GDAL-Python bindings
        NOTE: Do not run this method on data already in L2 level!
            Use get_mean_refl instead

        Parameters
        ----------
        sentinel_data_dir : String
            path to the directory that contains the Level-1C data. In case
            the data is zipped (default when downloaded from Copernicus) specify
            the file-path of the zip
        resolution : Integer
            spatial resolution of the atmospherically corrected imagery
            possible value: 10, 20, 60 meters
        storage_dir : String
            path to the directory the final layer stack should be moved to. If None,
            the layer stack will remain the sentinel_data_dir_l2 in the img folder


        Returns
        -------
        scene_id:
            ID of the processed Sentinel-2 scene
        """
        # returns file name of Sentinel-2 imagery in L2 level and the
        # file path to the metadata xml
        fname_s2, metadata_xml = call_gdal_merge(sentinel_data_dir,
                                              resolution,
                                              storage_dir=storage_dir)
        # with that information, the zonal statistics can be computed
        # using the provided shapefile with the object boundaries and
        # the landuser/ cover information
        # get the tablename of the object spectra table
        if self.__tablenames is None:
            self.set_tablenames()
        tablename_obj_spec = self.__tablenames[2]

        # parse the metadata and insert it into the database
        metadata = parse_s2xml(metadata_xml)
        insert_scene_metadata(metadata, use_gee=False, raster=fname_s2)
        # get the scene_id and the acquisition date
        scene_id = metadata['SCENE_ID']
        acqui_date = metadata['SENSING_TIME'][0:10]
        get_mean_refl(shp_file, fname_s2, acqui_date, scene_id,
                      tablename_obj_spec)
        # return the SCENE_ID
        return scene_id
