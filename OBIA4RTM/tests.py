#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat May  2 10:55:27 2020

@author: lukas
"""
import os
from OBIA4RTM.processing_api import API
from OBIA4RTM.install import install


class tests:
    """class providing some tests for checking if OBIA4RTM builds"""
    def __init__(self):
        self.api = API(use_gee=False)

    @staticmethod
    def checkIfInstalls():
        """check if OBIA4RTM backend installs correctly"""
        res = install.install()
        assert(res == 0)

    def checkHomeDir(self):
        """checks if the OBIA4RTM directory exists"""
        assert(os.path.isdir(self.api.obia4rtm_home))

    def checkTables(self):
        """checks if the table names are filled"""
        self.api.set_tablenames()
        assert(type(self.api.tablenames) == list)
        assert(len(self.api.tablenames) == 4)
        assert(self.api.tablenames != '')

    def checkConfigFile(self):
        """checks if config files have been copied to default directory"""
        assert(self.api.backend_cfg != '')
        assert(os.path.isfile(self.api.backend_cfg))

    def checkInvsersion(self)