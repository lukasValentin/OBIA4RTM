#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 10:43:55 2019

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
from os.path import expanduser
from shutil import copyfile
import OBIA4RTM
from OBIA4RTM.setup_db.setup_postgres import setupDataBase
from OBIA4RTM.setup_db.create_schema import create_schema


def install():
    """
    does a full-installation of OBIA4RTM backend facilities including the
    PostgreSQL database setup and copying of configuration files to a user-
    accessible directory
    NOTE: PostgreSQL must be almost installed as well as PostGIS
    """
    # firstly, try to setup the Postgres database for the backend
    # NOTE: PostgreSQL must be almost installed as well as PostGIS
    print('** Start to run OBIA4RTM installation script!')
    setup = setupDataBase()
    setup.setup_backend()
    
    # now determine the location to which the configuration files should be
    # copied to. This depends on the OS
    print('** Setup OBIA4RTM directory with configuration files!')
    home = expanduser("~")
    # try to make a OBIA4RTM directory in the home directory of the current user
    obia4rtm_dir = home + os.sep + 'OBIA4RTM'
    try:
        os.mkdir(obia4rtm_dir)
    except PermissionError:
        print('Failed to write to {}. Please check permissions!'.format(
                obia4rtm_dir))
        sys.exit(-1)
    # do the same for the logging directory
    log_dir = obia4rtm_dir + os.sep + 'log'
    try:
        os.mkdir(log_dir)
    except PermissionError:
        print('Failed to write to {}. Please check permissions!'.format(
                log_dir))
        sys.exit(-1)
    # note down the OBIA4RTM home dir
    OBIA4RTM_install_dir = os.path.dirname(OBIA4RTM.__file__)
    fname = OBIA4RTM_install_dir + os.sep + 'OBIA4RTM_HOME'
    with open(fname, "w") as out:
        out.write(obia4rtm_dir)
    # after that, copy the configuration files to this directory
    # these include the prosail.txt, obia4rtm_backened.cfg,
    # postgres.ini and landcover.cfg file as well as soil_reflectance.txt
    files_to_be_copied = ['prosail.txt', 'obia4rtm_backend.cfg', 'postgres.ini', 'landcover.cfg', 'soil_reflectance.txt']
    for file in files_to_be_copied:
        src = OBIA4RTM_install_dir + os.sep + file
        dst = obia4rtm_dir + os.sep + file
        copyfile(src, dst)
    print('** Base Setup of OBIA4RTM finished!')
    # setup a new schema and the schema-specific tables of OBIA4RTM
    res = create_schema()
    if res != 0:
        print('ERROR: Failed to setup a new schema for the OBIA4RTM database! '\
              'See log-file in {} for more details.'.format(
                      log_dir))
    else:
        print('** Success! OBIA4RTM is now ready for use!\nConfiguration files '\
              'can be found and modified in {}.'.format(obia4rtm_dir))
