#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 15:42:10 2019

This module is part of OBIA4RTM.

Copyright (c) 2019 Lukas Graf

@author: Lukas Graf, graflukas@web.de
"""
import os
import sys
import wget
import tarfile
import subprocess
from urllib.error import HTTPError
import Py6S
import OBIA4RTM


def install_6S(link=None):
    """
    installs the 6S algorithm required for atmospheric correction from
    the Fortran source code using gfortran.
    The sources will be installed to the OBIA4RTM install dir
    (somewhere in the user profile) where also the config files are stored.

    Currently, only Linux/ Unix systems are supported for this operation.

    In case you expire any problems automatically downloading and building
    6S, please also consult: https://py6s.readthedocs.io/en/latest/installation.html

    Windows-Users please note that the installation might not be that smoothly
    as on Posix, as you will have to install a bunch of additional functionalities
    """
    # first, find out where OBIA4RTM has been installed to
    obia4rtm_home = os.path.dirname(OBIA4RTM.__file__)
    print('** Trying to download and install 6S from Fortran source!')
    # read in the OBIA4RTM_HOME file to get the installation directory
    # the user has access to
    with open(obia4rtm_home + os.sep + 'OBIA4RTM_HOME', 'r') as data:
        install_dir = data.readline()
    # now try to setup a directory 6S can be installed to
    six6_dir = install_dir + os.sep + 'sixS'
    try:
        os.mkdir(six6_dir)
    except (FileExistsError, PermissionError) as err:
        print('Failed to create directory for installing 6S!\n{}'.format(
                err))
        sys.exit(-1)
    # change to the installation directory for 6S
    os.chdir(six6_dir)
    # try to setup a source and build directory
    try:
        os.mkdir('src')
    except FileExistsError as err:
        print('Failed to create directory for installing 6S!\n{}'.format(
                err))
    print('** Setup installation into {}'.format(six6_dir))
    # now the 6S source code can be downloaded (link last tested on 26th Jul 2019)
    # if this link is not working any longer, you can provide an alternative link
    # in the function call interface
    # before downloading, change to the src directory
    os.chdir('src')
    if link is None:
        link = "http://rtwilson.com/downloads/6SV-1.1.tar"
    # use wget to download the Fortran source code as tar file
    try:
        sixS_tar = wget.download(link)
    except HTTPError:
        print("The link address '{}' for downloading the 6S tar-ball seems not be valid!".format(
                link))
    # try to unpack the tarball
    try:
        tf = tarfile.open(sixS_tar)
        tf.extractall()
    except tarfile.TarError:
        print("The tar-file '{}' seems to be corrupt and cannot be unpacked!".format(
                sixS_tar))
    # after that a directory called 6SV1.1 should be created -> go into it
    sixS_dir = '6SV1.1'
    os.chdir(sixS_dir)
# =============================================================================
#     # now, the makefile must be altered to set the correct compiler option
#     # determine the OS as there are different ways to go for Win and posix
    platform = os.name
    with open('Makefile','r') as makefile:
             lines = makefile.readlines()
    if platform == 'nt':
         # Windows
         # iterate over the lines to determine and alter the FC flag
         line_number = 0
         for line in lines:
             line_number += 1
             if (line.find('-lm') != -1):
                 break
         # keep the previuos and following lines and only alter the 'FC' line
         prev_lines = lines[0:line_number-1]
         foll_lines = lines[line_number::]
         # according to https://py6s.readthedocs.io/en/latest/installation.html
         # the -lm option must be deleted
         line = line.replace('-lm','')
    else:
         # Linux and Mac OS X
         # this option will ONLY work under Linux, Unix and OS X given that
         # gfortran is available
        # iterate over the lines to determine and alter the FC flag
         line_number = 0
         for line in lines:
             line_number += 1
             if (line.startswith('FC')):
                 break
         # keep the previuos and following lines and only alter the 'FC' line
         prev_lines = lines[0:line_number-1]
         foll_lines = lines[line_number::]
         # instead of the old argument of the 'FC', this expression is required
         # according to https://py6s.readthedocs.io/en/latest/installation.html
         line = 'FC      = gfortran -std=legacy -ffixed-line-length-none -ffpe-summary=none $(FFLAGS)\n'
    # delete the old Makefile
    os.remove('Makefile')
    # no write to the new makefile
    with open('Makefile', 'x') as makefile:
        makefile.writelines(prev_lines)
        makefile.writelines(line)
        makefile.writelines(foll_lines)
# =============================================================================
    # run the make file (NOTE: make mus be installed on Win seperately!)
    try:
        print('** Running make to build the executable')
        p = subprocess.run('make')
    except Exception as err:
        print('Make failed!\n{}'.format(err))
    print('** Make run successfully completed- Trying to setup symbolic link to 6S binary')
    # finally, create a symbolic link to ensure that the binary can be assessed
    # again, distinguish between Win and Posix
    if platform == 'nt':
        os.system('MKLINK sixsV1.1.exe C:\Windows\System')
    else:
        os.system('ln sixsV1.1 /usr/local/bin/sixs')
    # finished
    print('** 6S source code successfully downloaded, unpacked and built!')
    # testing
    print('** Running test if 6S Python-Wrapper (Py6S) is working. Output:\n')
    Py6S.SixS.test()


# make the function executable when the module is called from the command line
if __name__ == '__main__':
    install_6S()
