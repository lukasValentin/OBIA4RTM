#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat May  2 10:55:27 2020

@author: lukas
"""
import os
import requests
from urllib.request import urlopen
from io import BytesIO
from zipfile import ZipFile

from OBIA4RTM.processing_api import API
from OBIA4RTM.install import install
from OBIA4RTM.mdata_proc.parse_s2xml import parse_s2xml
from OBIA4RTM.mdata_proc.insert_scene_metadata import insert_scene_metadata


class tests:
    """class providing some tests for checking if OBIA4RTM builds"""
    def __init__(self):
        self.api = API(use_gee=False)

    @staticmethod
    def _checkIfInstalls():
        """check if OBIA4RTM backend installs correctly"""
        res = install()
        assert(res == 0)

    def _checkHomeDir(self):
        """checks if the OBIA4RTM directory exists"""
        assert(os.path.isdir(self.api.obia4rtm_home))

    def _checkTables(self):
        """checks if the table names are filled"""
        self.api.set_tablenames()
        assert(type(self.api.tablenames) == list)
        assert(len(self.api.tablenames) == 4)
        assert(self.api.tablenames != '')

    def _checkConfigFile(self):
        """checks if config files have been copied to default directory"""
        assert(self.api.backend_cfg != '')
        assert(os.path.isfile(self.api.backend_cfg))

    def _checkInvsersion(self):
        """test case to run inversion on a very small subset of S2 scene"""
        # get zipped test data from GitHub
        # get zipped Sentinel-2 imagery
        imageURL = 'https://github.com/lukasValentin/OBIA4RTM/raw/master/Examples/data/S2A_20160718_subset.zip'
        resp = urlopen(imageURL)
        zipfile = ZipFile(BytesIO(resp.read()))
        imageFile = zipfile.namelist()[0]
        assert(imageFile != '')

        # get zipped shape file with field parcel boundaries
        shpURL = 'https://github.com/lukasValentin/OBIA4RTM/raw/master/Examples/data/SHP/2017_Multiply_Sample_Area_red.zip'
        resp = urlopen(shpURL)
        zipfile = ZipFile(BytesIO(resp.read()))
        shapeFile = zipfile.namelist()
        assert(len(shapeFile) > 0)
        shapeFile = [x for x in shapeFile if x.find('shp') != -1][0]
        assert(shapeFile != '')

        # define inversion settings for test scene
        scene_id = 'S2B_170718T101029_N0205_R022_T32UQU_20170718T101346'
        num_best_solutions = 10
        luc_classes = [0, 1, 2]

        # get scene metadata and store it in database
        xmlURL = 'https://github.com/lukasValentin/OBIA4RTM/raw/master/Examples/data/MTD_TL.xml'
        response = requests.get(xmlURL)
        with open('metadata.xml', 'wb') as xml_file:
            xml_file.write(response.content)
        # parse xml into dict and write to database
        metadata = parse_s2xml('metadata.xml')
        insert_scene_metadata(metadata, use_gee=False, raster=imageFile)

        # perform the actual inversion
        status = self.api.do_inversion(scene_id,
                                       num_best_solutions,
                                       luc_classes,
                                       return_specs=True)
        assert(status == 0)

    def run(self):
        """calls tests one by one"""
        self._checkIfInstalls()
        self._checkHomeDir()
        self._checkConfigFile()
        self._checkTables()
        self._checkInvsersion()


if __name__ == '__main__':
    tester = tests()
    tester.run()
