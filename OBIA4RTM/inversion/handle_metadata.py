#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 10:58:16 2019

This module is part of OBIA4RTM.

Copyright (c) 2019 Lukas Graf

"""
import sys
import numpy as np
from spectral import BandResampler
from OBIA4RTM.configurations.logger import close_logger


def get_bands(conn, cursor, sensor, logger):
    """
    reads in sensor band centers and FWHM stored in database

    Parameters
    ----------
    conn : psycopg2 Database connection
        connection to OBIA4RTM PostgreSQL database
    cursor : psycopg2 Database cursor
        cursor for DB inserts and queries
    sensor : String
        name of the sensor; currently either 'S2A' or 'S2B'
    logger : logging Logger
        for recording errors to the log file

    Returns
    -------
    centers : List
        list of central wavelengths of the spectral bands of the sensor (nm)
    fwhm : List
        list of the full width half maximum of the spectral bands (nm)
    """
    query = "SELECT central_wvl, band_width FROM public.s2_bands WHERE " \
            "sensor = '{0}' ORDER by central_wvl;".format(
                    sensor)
    try:
        cursor.execute(query)
        data = cursor.fetchall()
        centers = [item[0] for item in data]
        fwhm = [item[1] for item in data]
    except ValueError:
        logger.error("Could not retrieve sensor metatdata!", exc_info=True)
        close_logger(logger)
        sys.exit(-1)
    # endif
    return centers, fwhm
# end get_s2band


def get_resampler(conn, cursor, sensor, logger):
    """
    get the spectral properties of a sensor and generate a resampler object.
    Currently, Sentinel-2A and Sentinel-2B are supported

    Parameters
    ----------
    conn : psycopg2 Database connection
        connection to OBIA4RTM PostgreSQL database
    cursor : psycopg2 Database cursor
        cursor for DB inserts and queries
    sensor : String
        name of the sensor; currently either 'S2A' or 'S2B'
    logger : logging Logger
        for recording errors to the log file

    Returns
    -------
    resampler : spectral BandResampler
        Resampler Object for resampling the ProSAIL output to the spectral
        resolution of Sentinel-2
    """
    # get S2 sensor-response function
    centers, fwhm = get_bands(conn, cursor, sensor, logger)
    # define centers and bandwith of prosail output
    centers_prosail = np.arange(400,2501,1)
    fwhm_prosail = np.ones(centers_prosail.size)
    # crate a new resampler object to convert the 1nm spectra to the spectral
    # resolution of Sentinel-2
    resampler = BandResampler(centers_prosail, centers, fwhm1=fwhm_prosail, fwhm2=fwhm)
    return resampler
# end get_resampler
