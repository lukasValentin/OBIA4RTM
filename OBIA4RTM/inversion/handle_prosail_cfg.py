#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 13 11:14:32 2019

This module is part of OBIA4RTM.

Copyright (c) 2019 Lukas Graf

@author: Lukas Graf, graflukas@web.de
"""
import sys
from configparser import ConfigParser
import numpy as np
from OBIA4RTM.configurations.logger import close_logger


def get_landcover_classes(landcover_cfg):
    """
    get the number and names of the land cover classes
    stored in the ProSAIL.cfg file

    Parameters
    ----------
    cfg_file : String
        path to the land cover configuration file

    Returns
    -------
    luc_classes : List
        list of landcover classes (code + semantics)
    """
    parser = ConfigParser()
    parser.read(landcover_cfg)
    # get the land use classes in the cfg file
    section = parser.sections()
    landcover_classes = list(parser.items(section[0]))
    return landcover_classes
# end get_landcover_classes


def read_params_per_class(prosail_cfg, landcover_cfg, logger):
    """
    reads in the vegetation parameters for the ProSAIL model for each
    land cover class

    Parameters
    ----------
    cfg_file : String
        path to the ProSAIL configurations file
    landcover_cfg : String
        path to the landcover configuration file
    logger : logging.Logger
        for recording errors

    Returns
    -------
    container : Dictionary
        dict with the ProSAIL parameters per land cover class
    """
    luc_classes = get_landcover_classes(landcover_cfg)
    # now read in the actual data
    n_classes = len(luc_classes)  # number of land cover classes
    try:
        assert n_classes >= 1
    except AssertionError:
        logger.error('Error: >=1 land cover class must be provided!',
                     exc_info=True)
        close_logger(logger)
        sys.exit(-1)
    num_lines_per_luc = 13        # number of lines per land cover class
    offset_rows = 2               # number of rows to be skipped when reading
    footer_rows = (n_classes - 1) * (num_lines_per_luc)
    # loop over the land cover classes, store results in dictionary
    container = dict()
    try:
        for section in luc_classes:
            # read in the params per land cover class using numpy
            # class_name = section[1]
            values = np.genfromtxt(prosail_cfg,
                                   skip_header=offset_rows,
                                   skip_footer=footer_rows)
            # store in "container" dictionary
            container[section] = values
            # increment offset_rows and footer_rows for next iteration
            offset_rows =+ num_lines_per_luc + 2
            footer_rows =- (num_lines_per_luc + 2)
    except ValueError:
        logger.error('Failed to read in the config-File', exc_info=True)
        close_logger(logger)
        sys.exit(-1)
    return container
# end read_params_per_class

