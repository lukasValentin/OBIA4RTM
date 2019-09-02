#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 12:32:24 2019

This module is part of OBIA4RTM.
It is part of the (optional) Sen2Core preprocessing wrapper addon that takes
care about image preprocessing (i.e atmospheric correction) using Sen2Core
software (see: http://step.esa.int/main/third-party-plugins-2/sen2cor/)

NOTE: Sen2Core must be installed on your computer!

NOTE: Windows users might have to add the GDAL binaries (they come with OSGEO)
to their PATH variable

Copyright (c) 2019 Lukas Graf

@author: Lukas Graf, graflukas@web.de
"""
import os
import re
import sys
import shutil
import subprocess
from zipfile import ZipFile
from OBIA4RTM.configurations.logger import get_logger, close_logger


error_message = 'Sen2Core preprocessing failed. Check log.'


def check_sen2core_installation(path):
    """
    check if Sen2Core is installed and can be used

    Parameters
    ----------
    path : String
        user-provided path to Sen2Core installation directory
    Returns
    -------
    exists : Boolean
        True, if directory exists and False if tests fail
    cmd : String
        command for testing if Sen2Core is working
    """
    # check if the directory as such exists
    if not os.path.isdir(path):
        print("The system cannot find the specified path: '{}'".format(
                path))
        exists = False
    # check if L2A_Process command can be executed
    # make distinction between Windows and Linux/ OS X (-> posix)
    platform = os.name
    if platform == 'posix':
        cmd = path + os.sep + 'bin' + os.sep + 'L2A_Process --help'
    else:
        cmd = path + os.sep + 'L2A_Process.bat --help'
    # try to execute the command
    out = subprocess.Popen(cmd,
                           shell=True,
                           stderr=subprocess.PIPE,
                           stdout=subprocess.PIPE)
    res = out.communicate()
    # read the output of the stderr from the pipe
    stderr = res[1].decode()
    # check if an error was produced
    if stderr != '':
        print('Sen2Core seems not be installed in the specified path!')
        exists = False
    # otherwise everything should work
    exists = True
    return exists, cmd


def call_sen2core(sentinel_data_dir, zipped, resolution, path_sen2core):
    """
    calls Sen2Core and runs it on a downloaded Sentinel 1C dataset to
    convert it to Level 2A.
    The output spatial resolution must be provided (10, 20 or 60 meters)

    NOTE: If you have already L2 imagery then only run the gdal_merge wrapper
    and to not use this function

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

    Returns
    -------
    sentinel_data_dir_l2
    """
    # check inputs
    if zipped:
        if not os.path.isfile(sentinel_data_dir):
            print("Error: '{}' does not exist!".format(
                    sentinel_data_dir))
            sys.exit(-1)
    else:
        if not os.path.isdir(sentinel_data_dir):
            print("Error: '{}' does not exist!".format(
                    sentinel_data_dir))
            sys.exit(-1)
    # check specified spatial resolution of the result
    allowed_res = [10, 20, 60]  # m
    if resolution not in allowed_res:
        print("Error: The specified spatial resolution of {0} is not allowed!\n"\
              "Must be one of {1}!".format(resolution, allowed_res))
        sys.exit(-1)
    # check if Sen2Core is installed and working
    runs, cmd = check_sen2core_installation(path_sen2core)
    if not runs:
        print('Error: Sen2Core seems not to work properly!')
        sys.exit(-1)
    # after that, enable logging
    logger = get_logger()
    logger.info('Setting up Sen2Core processing environment for processing '\
                '{}'.format(sentinel_data_dir))
    # if the data is still zipped unzip
    if zipped:
        # extract the parent directory
        parent_dir = os.path.dirname(sentinel_data_dir)
        # unzip
        zip_file = ZipFile(sentinel_data_dir)
        zip_file.extractall(parent_dir)
        zip_file.close()
        # check if everything is OK
        # new name of sentinel_data_dir is now without ending .zip
        sentinel_data_dir = sentinel_data_dir.replace('.zip', '')
        # should be a directory
        if not os.path.isdir(sentinel_data_dir):
            logger.error('Unpacking of Sentinel-2 data failed!')
            close_logger(logger)
            sys.exit(error_message)
        logger.info("Successfully extracted zipped data to {}".format(
                sentinel_data_dir))
    # endif
    # now the data is ready for Sen2Core
    # create the command to run Sen2Core
    cmd = cmd.replace(' --help', '')
    cmd = cmd + ' ' + sentinel_data_dir + ' --resolution=' + str(resolution)
    # call Sen2Core
    # try to execute the command
    logger.info('Starting Sen2Core processing')
    out = subprocess.Popen(cmd,
                           shell=True,
                           stderr=subprocess.PIPE,
                           stdout=subprocess.PIPE)
    # read the communication of the process
    res = out.communicate()
    stdout = res[0].decode()
    stderr = res[1].decode()
    # write output to file
    # determine the filename
    sub_pos = [m.start() for m in re.finditer('_', sentinel_data_dir)]
    fname = sentinel_data_dir[0:sub_pos[2]]

    # parent directory
    parent_dir = os.path.dirname(sentinel_data_dir)
    # save output of Sen2Core
    sen2core_stderr = parent_dir + os.sep + 'Sen2Core_' + os.path.basename(fname) + '.stdout'
    with open(sen2core_stderr, 'a') as out:
        out.writelines(stdout)

    sen2core_stdout = parent_dir + os.sep + 'Sen2Core_' + os.path.basename(fname) + '.stderr'
    with open(sen2core_stdout, 'a') as out:
        if stderr == '':
            stderr = 'Sen2Core terminated without errors'
        out.writelines(stderr)

    # determine the dir-name of the processed data
    fname = fname.replace('MSIL1C', 'MSIL2A')
    # get list of all directories
    list_dirs = os.listdir(parent_dir)
    # directory of the L2 data
    sentinel_data_dir_l2 = ''
    for directory in list_dirs:
        sub_pos = [m.start() for m in re.finditer('_', directory)]
        fname_act = parent_dir + os.sep + directory[0:sub_pos[2]]
        if fname_act == fname:
            sentinel_data_dir_l2 = parent_dir + os.sep + directory
            break
    if sentinel_data_dir_l2 == '':
        logger.error('Seems as if Sen2Core failed. Check {} for more info.'.format(
                sen2core_stdout))
        close_logger(logger)
        sys.exit(error_message)
    logger.info("Success - Processed data is in '{0}. See also {1}'".format(
            sentinel_data_dir_l2,
            sen2core_stdout))
    # delete the L1C directory in case the data was available as zip to
    # save disk storage
    if zipped:
        shutil.rmtree(sentinel_data_dir, ignore_errors=True)
    close_logger(logger)
    return sentinel_data_dir_l2


def call_gdal_merge(sentinel_data_dir_l2, resolution, storage_dir=None):
    """
    calls the gdal_merge.py script to make an image layer stack and prepare
    the imagery for usage in OBIA4RTM.
    Outputs a GeoTiff with the nine Sentinel-2 bands used in OBIA4RTM
    and the SCL band that contains the preclassification information.

    You can use this function also if you L2 data

    Parameters
    ----------
    sentinel_data_dir_l2 : String
        path of the directory containing the output of sen2core in L2 level
    resolution : Integer
        spatial resolution of the atmospherically corrected imagery
        possible value: 10, 20, 60 meters
    storage_dir : String
        path to the directory the layer stack should be moved to. If None,
        the layer stack will remain the sentinel_data_dir_l2 in the img folder

    Returns
    -------
    fname_stack : String
        file-path to the stacked imagery
    metadata_xml : String
        file-path to the metadata xml file
    """
    # enable logging
    logger = get_logger()
    # check inputs
    if not os.path.isdir(sentinel_data_dir_l2):
        logger.error("Error: '{}' does not exist!".format(
                sentinel_data_dir_l2))
        close_logger(logger)
        sys.exit(error_message)
    # resolution
    allowed_res = [10, 20, 60]  # m
    if resolution not in allowed_res:
        logger.error("Error: The specified spatial resolution of {0} is not allowed! "\
              "Must be one of {1}!".format(resolution, allowed_res))
        sys.exit(error_message)
    # storage directory
    if storage_dir is not None:
        if not os.path.isdir(storage_dir):
            try:
                os.mkdir(storage_dir)
            except PermissionError:
                logger.error("Could not create directory '{}'".format(
                        sentinel_data_dir_l2), exc_info=True)

    logger.info('Formatting sen2core output for OBIA4RTM')
    # change to the sentinel_data_dir_l2 to avoid endless path names
    # jump directly into the 'Granule directory'
    sentinel_data_dir_l2 = sentinel_data_dir_l2 + os.sep + 'GRANULE'
    os.chdir(sentinel_data_dir_l2)
    # path to the image bands
    next_subdir = os.listdir()[0]
    # now the full path can be constructed
    sentinel_data_dir_l2 += os.sep + next_subdir
    os.chdir(sentinel_data_dir_l2)
    # check if the MTD_TL.xml metadata file can be found
    if not os.path.isfile('MTD_TL.xml'):
        logger.warning('No metadata-xml file could be found!')
        metadata_xml = ''
    else:
        metadata_xml = sentinel_data_dir_l2 + os.sep + 'MTD_TL.xml'

    sentinel_data_dir_l2 += os.sep + 'IMG_DATA' + os.sep + 'R' + str(resolution) + 'm'
    try:
        os.chdir(sentinel_data_dir_l2)
    except FileNotFoundError:
        logger.error('Could not find {}'.format(sentinel_data_dir_l2),
                     exc_info=True)
        close_logger(logger)
        sys.exit(error_message)
    # get the jp2 files containing the single bands and the SCL information
    band_files = os.listdir()
    band_names = ['B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B8A', 'B11', 'B12', 'SCL']
    stack_files = []
    # loop over the filenames to find the important ones
    for band_file in band_files:
        for band_name in band_names:
            if band_file.find(band_name) != -1:
                stack_files.append(band_file)
                break
    # now the list must be sorted to bring the bands in the correct order
    stack_files.sort()
    # check if 10 bands were found
    try:
        assert len(stack_files) == 10
    except AssertionError:
        logger.error('Expected 10 bands got {}'.format(len(stack_files)),
                     exc_info=True)
        close_logger(logger)
        sys.exit(error_message)
    # convert list to string
    stack_files = str(stack_files).replace('[','').replace(']','').replace(',', ' ')
    # make name of stacked layer file
    sub_pos = [m.start() for m in re.finditer('_', band_files[0])]
    prefix = band_files[0][0:sub_pos[1]]
    fname_stack = prefix + '_merged.tiff'
    # now everything is ready for running the gdal_merge.py script
    # output is GTiff and not Jpeg2000 as there are still some driver problems
    cmd = 'gdal_merge.py -of GTiff -separate ' + stack_files + ' -o ' + fname_stack
    logger.info('Running {}'.format(cmd))
    out = subprocess.Popen(cmd,
                           shell=True,
                           stderr=subprocess.PIPE,
                           stdout=subprocess.PIPE)
    res = out.communicate()
    stderr = res[1].decode()
    # check if the command worked
    if stderr != '':
        logger.error('gdal_merge failed: {}'.format(stderr))
        close_logger(logger)
        sys.exit(error_message)
    logger.info('Successfully stacked Sentinel-2 bands ({})'.format(fname_stack))
    # give the full path
    fname_stack_short = fname_stack
    fname_stack = sentinel_data_dir_l2 + os.sep + fname_stack
    # in case an alternative directory was specified move the metadate file and
    # the stacked layer file to this directory
    if storage_dir is not None:
        # rename the metadata-file and copy it to the storage drive
        copy = shutil.copy2(metadata_xml, storage_dir + os.sep + prefix + '_MTD_TL.xml')
        try:
            assert copy != ''
            assert copy is not None
        except AssertionError:
            logger.error('Copying of metafile failed!', exc_info=True)
            close_logger(logger)
            sys.exit(error_message)
        # move the stacked image
        os.rename(fname_stack, storage_dir + os.sep + fname_stack_short)
        logger.info("Moved the imagery and the metadata xml to '{}'".format(
                storage_dir))
    # close the logger
    close_logger(logger)
    # return the file-paths of the imagery and the metadata
    return fname_stack, metadata_xml


def do_sen2core_preprocessing(sentinel_data_dir, zipped, resolution, path_sen2core,
                              storage_dir=None):
    """
    calls the sen2core wrapper and the gdal_merge wrapper to carry out the
    atmospheric correction and preclassification on Sentinel-1 imagery
    (L1C level) required for OBIA4RTM.

    NOTE: If you have already L2 imagery then only run the gdal_merge wrapper
    and to not use this function
    Make also sure that gdal_merge can be executed from the command line.

    NOTE: Windows users might have add the gdal binaries to their PATH!!

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
    fname_stack : String
        file-path to the stacked imagery (required in OBIA4RTM)
    metadata_xml : String
        file-path to the metadata xml file (required in OBIA4RTM)
    """
    # run sen2core for atmospheric correction and preclass
    sentinel_data_dir_l2 = call_sen2core(sentinel_data_dir,
                                         zipped,
                                         resolution,
                                         path_sen2core)
    # make image stack and identify metadata xml file
    fname_stack, metadata_xml = call_gdal_merge(sentinel_data_dir_l2,
                                              resolution,
                                              storage_dir=storage_dir)
    # return image stack file-path and metadata file path
    # -> now the data can be used in OBIA4RTM
    return fname_stack, metadata_xml
