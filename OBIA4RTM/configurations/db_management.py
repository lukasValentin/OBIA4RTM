#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 15:38:37 2019

This module is part of OBIA4RTM.

Copyright (c) 2019 Lukas Graf

@author: Lukas Graf, graflukas@web.de
"""
import sys
import os
import OBIA4RTM
from OBIA4RTM.configurations.connect_db import connect_db, close_db_connection
from OBIA4RTM.configurations.logger import get_logger, close_logger
from OBIA4RTM.inversion.handle_prosail_cfg import get_landcover_classes


def update_luc_table(landcover_table, landcover_cfg=None):
    """
    updates the land-cover/ land use table in OBIA4RTM that is required for
    performing land-cover class specific vegetation parameter retrieval
    Make sure that the classes in the config file match the land cover classes
    provided for the image objects and used for generating the lookup-table.
    Otherwise bad things might happen.

    NOTE: in case land cover classes that are about to be inserted are already
    stored in the table, they will be overwritten!

    Parameters
    ----------
    landcover_table : String
        name of the table with the land cover information (<schema.table>)
    landcover_cfg : String
        file-path to land cover configurations file

    Returns
    -------
    None
    """
    # open the logger
    logger = get_logger()
    # if no other file is specified the default file from the OBIA4RTM
    # directory in the user profile will be used (landcover.cfg)
    if landcover_cfg is None:
        # determine the directory the configuration files are located
        obia4rtm_dir = os.path.dirname(OBIA4RTM.__file__)
        fname = obia4rtm_dir + os.sep + 'OBIA4RTM_HOME'
        with open(fname, 'r') as data:
            directory = data.readline()
        landcover_cfg = directory + os.sep + 'landcover.cfg'
    # check if specified file exists
    if not os.path.isfile(landcover_cfg):
        logger.error('The specified landcover.cfg cannot be found!',
                     exc_info=True)
        close_logger(logger)
        sys.exit('Error during inserting landcover information. Check log!')
    # connect database
    con, cursor = connect_db()
    # read the landcover information
    luc_classes = get_landcover_classes(landcover_cfg)
    # now read in the actual data
    n_classes = len(luc_classes)  # number of land cover classes
    try:
        assert n_classes >= 1
    except AssertionError:
        logger.error('Error: >=1 land cover class must be provided!',
                     exc_info=True)
        close_logger(logger)
        sys.exit('Error while reading the landcover.cfg file. Check log.')
    # now, iterate through the lines of the cfg files and insert it into
    # the Postgres database
    logger.info("Try to insert values into table '{0}' from landcover.cfg "\
                "file ({1})".format(
            landcover_table,
            landcover_cfg))

    for luc_class in luc_classes:
        # the first item of the tuple must be an integer value
        # the second one a string
        try:
            luc_code = int(luc_class[0])
        except ValueError:
            logger.error('Landcover.cfg file seems to be corrupt. '\
                         'Excepted integer for land cover code!',
                         exc_info=True)
            close_logger(logger)
            sys.exit('Error during inserting landcover.cfg. Check log!')
        try:
            luc_desc = luc_class[1]
        except ValueError:
            logger.error('Landcover.cfg file seems to be corrupt. '\
                         'Excepted string for land cover description!',
                         exc_info=True)
            close_logger(logger)
            sys.exit('Error during inserting landcover.cfg. Check log!')
        # insert into database
        # ON CONFLICT -> old values will be replaced
        sql = "INSERT INTO {0} (landuse, landuse_semantic) VALUES ({1},'{2}')"\
            " ON CONFLICT (landuse) DO UPDATE SET landuse = {1},"\
            " landuse_semantic = '{2}';".format(
                    landcover_table,
                    luc_code,
                    luc_desc)
        cursor.execute(sql)
        con.commit()

    # close the logger and database connection afterwards
    logger.info("Updated land cover information in table '{}'".format(
            landcover_table))
    close_logger(logger)
    close_db_connection(con, cursor)
