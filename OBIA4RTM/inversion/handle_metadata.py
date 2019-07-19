#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 10:58:16 2019

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
from spectral import BandResampler
import numpy as np


def get_bands(conn, cursor, sensor):
    """
    reads in sensor band centers and FWHM stored in database
    """
    query = "SELECT central_wvl, band_width FROM s2_bands WHERE " \
            "sensor = '{0}' ORDER by central_wvl;".format(
                    sensor)
    try:
        cursor.execute(query)
        data = cursor.fetchall()
        centers = [item[0] for item in data]
        fwhm = [item[1] for item in data]
    except (ValueError) as err:
        print("Could not retrieve sensor metatdata! \n{}".format(err))
    # endif
    return centers, fwhm
# end get_s2band


def get_resampler(conn, cursor, sensor):
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
        in case of Sentinel-2 either "S2A" or "S2B"

    Returns
    -------
    resampler : spectral BandResampler
        Resampler Object for resampling the ProSAIL output to the spectral
        resolution of Sentinel-2
    """
    # get S2 sensor-response function
    centers, fwhm = get_bands(conn, cursor, sensor)
    # define centers and bandwith of prosail output
    centers_prosail = np.arange(400,2501,1)
    fwhm_prosail = np.ones(centers_prosail.size)
    # crate a new resampler object to convert the 1nm spectra to the spectral
    # resolution of Sentinel-2
    resampler = BandResampler(centers_prosail, centers, fwhm1=fwhm_prosail, fwhm2=fwhm)
    return resampler
# end get_resampler
