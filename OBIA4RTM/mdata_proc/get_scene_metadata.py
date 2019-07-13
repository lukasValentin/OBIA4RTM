#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  6 13:09:42 2019

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
import numpy as np


def get_sensor_and_sceneid(sensor_data):
    """
    extract the sensor name and scene_id from the metadata

    Parameters
    ----------
    sensor_data : dict
        extracted S2 metadata

    Returns
    -------
    Sensor : String
        name of the sensor
    Scene_ID : String
        name of the current scene
    """
    sensor = sensor_data['SENSOR']
    scene_id = sensor_data['SCENE_ID']
    return sensor, scene_id


def get_mean_angles(sensor_data):
    """
    get mean sensor azimuth and zenith angles for further setup
    of RTM and proper metadata storage
    only deal with those bands that are used for the plant parameter retrieval

    Parameters
    ----------
    sensor_data : dict
        extracted S2 metadata

    Returns
    -------
    m_sensor_azimuth : Float
        Azimuth angle (deg) of the sensor averaged over all relevant 9 S2-Bands
    m_sensor_zenith : Float
        Zenith angle (deg) of the sensor averaged over all relevant 9 S2-Bands
    m_rel_azimuth : Float
        Relative Azimuth angle (deg) between the sensor and the sun
    """
    # sensor azimuth angle (deg)
    BANDS = 9
    m_sensor_azimuth = np.float32(sensor_data['AZIMUTH_1'])   # Band 2
    m_sensor_azimuth += np.float32(sensor_data['AZIMUTH_2'])  # Band 3
    m_sensor_azimuth += np.float32(sensor_data['AZIMUTH_3'])  # Band 4
    m_sensor_azimuth += np.float32(sensor_data['AZIMUTH_4'])  # Band 5
    m_sensor_azimuth += np.float32(sensor_data['AZIMUTH_5'])  # Band 6
    m_sensor_azimuth += np.float32(sensor_data['AZIMUTH_6'])  # Band 7
    m_sensor_azimuth += np.float32(sensor_data['AZIMUTH_8'])  # Band 8A
    m_sensor_azimuth += np.float32(sensor_data['AZIMUTH_11'])  # Band 11
    m_sensor_azimuth += np.float32(sensor_data['AZIMUTH_12'])  # Band 12
    m_sensor_azimuth = m_sensor_azimuth / BANDS
    
    # sensor zenith angle (deg)
    m_sensor_zenith = np.float32(sensor_data['ZENITH_1'])   # Band 2
    m_sensor_zenith += np.float32(sensor_data['ZENITH_2'])  # Band 3
    m_sensor_zenith += np.float32(sensor_data['ZENITH_3'])  # Band 4
    m_sensor_zenith += np.float32(sensor_data['ZENITH_4'])  # Band 5
    m_sensor_zenith += np.float32(sensor_data['ZENITH_5'])  # Band 6
    m_sensor_zenith += np.float32(sensor_data['ZENITH_6'])  # Band 7
    m_sensor_zenith += np.float32(sensor_data['ZENITH_8'])  # Band 8A
    m_sensor_zenith += np.float32(sensor_data['ZENITH_11'])  # Band 11
    m_sensor_zenith += np.float32(sensor_data['ZENITH_12'])  # Band 12
    m_sensor_zenith = m_sensor_zenith / BANDS

    # calculate the relative azimuth (always provide the absolute value)
    m_rel_azimuth = abs(np.float32(sensor_data['AZIMUTH_SUN']) - m_sensor_azimuth)
    return m_sensor_zenith, m_rel_azimuth


def get_sun_zenith_angle(sensor_data):
    """
    extract the sensor zenith angle, required for RTM setup

    Parameters
    ----------
    sensor_data : Dictionary
        extracted S2 metadata

    Returns
    ------
    tts : Float32
        extracted sun zenith angle
    """
    tts = np.float32(sensor_data['ZENITH_SUN'])
    return tts


def get_acqusition_time(sensor_data):
    """
    extract the exact acqusition time of the scene and extract the date

    Parameters
    ----------
    sensor data : Dictionary
        extracted S2 metadata

    Returns
    -------
    acquistion_time : timestamp
        Exact time-stamp of scene acquisition
    acquistion_date : date
        date extracted of the acquistion timestamp
    """
    acquisition_time = sensor_data['SENSING_TIME']
    acqusition_date = acquisition_time[0:10]
    return acquisition_time, acqusition_date


def get_scene_footprint(sensor_data):
    """
    get the footprint (geometry) of a scene by calculating its geogr. extent

    Parameters
    ----------
    sensor data : Dictionary
        extracted S2 metadata

    Returns
    -------
    postgis_expression : String
        footprint with information for well-known-text based insert into PostGIS
    """
    pixelsize = 10  # meters
    # use per default the 10m-representation
    epsg = sensor_data['EPSG']
    epsg = epsg.split(':')[1]
    ulx = np.float32(sensor_data['ULX_10m'])  # upper left x
    uly = np.float32(sensor_data['ULY_10m'])  # upper left y
    nrows = int(sensor_data['NROWS_10m'])     # number of rows
    ncols = int(sensor_data['NCOLS_10m'])     # number of columns
    # calculate the other image corners (upper right, lower left, lower right)
    urx = ulx + (ncols - 1) * pixelsize       # upper right x
    ury = uly                                 # upper right y
    llx = ulx                                 # lower left x
    lly = uly - (nrows + 1) * pixelsize       # lower left y
    lrx = urx                                 # lower right x
    lry = lly                                 # lower right y
    # use the pairs to construct an insert statement for PostGIS
    ul = str(ulx) + " " + str(uly)
    ur = str(urx) + " " + str(ury)
    lr = str(lrx) + " " + str(lry)
    ll = str(llx) + " " + str(lly)
    postgis_expression = "ST_GeomFromText('POLYGON(({0},{1},{2},{3},{0}))', "\
        "{4})".format(
            ul, ur, lr, ll, epsg)
    return postgis_expression
