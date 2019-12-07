#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 09:26:21 2019

This module is part of OBIA4RTM.

Copyright (c) 2019 Lukas Graf

@author: Lukas Graf, graflukas@web.de
"""
import sys
import datetime


def parse_gee_metadata(gee_metadata):
    """
    parses Google-Earth-Engine (GEE) derived scene metadata into a dictionary
    structure parseable by subsequent analysis steps in OBIA4RTM

    Parameters
    ----------
    gee_metadata : Dictionary
        dictionary containing the GEE derived metadata that needs to be modified
        for usage in OBIA4RTM (especially be get_scene_metadata.py)

    Returns
    -------
    metadata : Dictionary
        formatted dictionary
    """
    # check the input first
    try:
        assert gee_metadata is not None
        assert type(gee_metadata) == dict
    except AssertionError:
        print('GEE metadata must not be empty and must be of type dict')
        sys.exit(-1)

    # empty dictionary for storing the re-formatted GEE metadata
    metadata = dict()
    # extract and format the sensor
    sensor = gee_metadata['SPACECRAFT_NAME']
    # convert Sentinel-2A to S2A and the same for Sentinel-2B
    if sensor == 'Sentinel-2A':
        metadata['SENSOR'] = 'S2A'
    elif sensor == 'Sentinel-2B':
        metadata['SENSOR'] = 'S2B'
    else:
        raise NotImplemented
    # SCENE_ID
    metadata['SCENE_ID'] = gee_metadata['PRODUCT_ID']
    # sensor looking angles (azimuth and zenith)
    # AZIMUTH
    metadata['AZIMUTH_1'] = gee_metadata['MEAN_INCIDENCE_AZIMUTH_ANGLE_B2']
    metadata['AZIMUTH_2'] = gee_metadata['MEAN_INCIDENCE_AZIMUTH_ANGLE_B3']
    metadata['AZIMUTH_3'] = gee_metadata['MEAN_INCIDENCE_AZIMUTH_ANGLE_B4']
    metadata['AZIMUTH_4'] = gee_metadata['MEAN_INCIDENCE_AZIMUTH_ANGLE_B5']
    metadata['AZIMUTH_5'] = gee_metadata['MEAN_INCIDENCE_AZIMUTH_ANGLE_B6']
    metadata['AZIMUTH_6'] = gee_metadata['MEAN_INCIDENCE_AZIMUTH_ANGLE_B7']
    metadata['AZIMUTH_8'] = gee_metadata['MEAN_INCIDENCE_AZIMUTH_ANGLE_B8A']
    metadata['AZIMUTH_11'] = gee_metadata['MEAN_INCIDENCE_AZIMUTH_ANGLE_B11']
    metadata['AZIMUTH_12'] = gee_metadata['MEAN_INCIDENCE_AZIMUTH_ANGLE_B12']
    # ZENITH
    metadata['ZENITH_1'] = gee_metadata['MEAN_INCIDENCE_ZENITH_ANGLE_B2']
    metadata['ZENITH_2'] = gee_metadata['MEAN_INCIDENCE_ZENITH_ANGLE_B3']
    metadata['ZENITH_3'] = gee_metadata['MEAN_INCIDENCE_ZENITH_ANGLE_B4']
    metadata['ZENITH_4'] = gee_metadata['MEAN_INCIDENCE_ZENITH_ANGLE_B5']
    metadata['ZENITH_5'] = gee_metadata['MEAN_INCIDENCE_ZENITH_ANGLE_B6']
    metadata['ZENITH_6'] = gee_metadata['MEAN_INCIDENCE_ZENITH_ANGLE_B7']
    metadata['ZENITH_8'] = gee_metadata['MEAN_INCIDENCE_ZENITH_ANGLE_B8A']
    metadata['ZENITH_11'] = gee_metadata['MEAN_INCIDENCE_ZENITH_ANGLE_B11']
    metadata['ZENITH_12'] = gee_metadata['MEAN_INCIDENCE_ZENITH_ANGLE_B12']
    # sun angles
    metadata['AZIMUTH_SUN'] = gee_metadata['MEAN_SOLAR_AZIMUTH_ANGLE']
    metadata['ZENITH_SUN'] = gee_metadata['MEAN_SOLAR_ZENITH_ANGLE']
    # extract sensing time -> use system-start time
    sensing_time = datetime.datetime.utcfromtimestamp(
                    gee_metadata['system:time_start'] / 1000)
    # convert to string
    sensing_time = sensing_time.strftime('%Y-%m-%dT%H:%M:%S.%msZ')
    metadata['SENSING_TIME'] = sensing_time
    # process the footprint information
    footprint = gee_metadata['system:footprint']
    # extract the geometry type and the coordinates
    geom_coor = footprint.get('coordinates')
    # find min and max lat as well as lon coordinates
    lat_min, lat_max = 999., -999.
    lon_min, lon_max = 999., -999.,
    for coor in geom_coor:
        lon = coor[0]
        lat = coor[1]
        # compare against to actual min and max
        if lon < lon_min:
            lon_min = lon
        if lon > lon_max:
            lon_max = lon
        if lat < lat_min:
            lat_min = lat
        if lat > lat_max:
            lat_max = lat
    # the EPSG code of the GEE data is per default WGS-84 (?)
    metadata['EPSG'] = 'EPSG:4326'
    # store the corner coordinates
    # upper left and lower right corner
    metadata['ULX_10m'] = lon_min
    metadata['ULY_10m'] = lat_max
    metadata['LRX_10m'] = lon_max
    metadata['LRY_10m'] = lat_min
    # some other parameters made available by GEE
    # NOTE: there is not so much information avaiable as from Sen2Core
    # as the atmospheric correction using GEE and 6S works differently
    metadata['CLOUDY_PIXEL_PERCENTAGE'] = gee_metadata['CLOUDY_PIXEL_PERCENTAGE']
    metadata['GRANULE'] = gee_metadata['MGRS_TILE']
    # also get the metadata from the atmospheric correction
    # surround with try-except in case the atcorr was not made before
    try:
        metadata['WATER_VAPOUR'] = gee_metadata['WATER_VAPOUR']
        metadata['OZONE'] = gee_metadata['OZONE']
        metadata['AOT'] = gee_metadata['AOT']
    except KeyError:
        pass
    # more GEE quality information -> might be helpful afterwards
    try:
        metadata['RADIOMETRIC_QUALITY_FLAG'] = gee_metadata['RADIOMETRIC_QUALITY_FLAG']
    except KeyError:
        pass
    try:
        metadata['REFLECTANCE_CONVERSION_CORRECTION'] = gee_metadata['REFLECTANCE_CONVERSION_CORRECTION']
    except KeyError:
        pass
    try:
        metadata['SENSOR_QUALITY_FLAG'] = gee_metadata['SENSOR_QUALITY_FLAG']
    except KeyError:
        pass
    # solar irradiance (W/m2)
    metadata['SOLAR_IRRADIANCE_B2'] = gee_metadata['SOLAR_IRRADIANCE_B2']
    metadata['SOLAR_IRRADIANCE_B3'] = gee_metadata['SOLAR_IRRADIANCE_B3']
    metadata['SOLAR_IRRADIANCE_B4'] = gee_metadata['SOLAR_IRRADIANCE_B4']
    metadata['SOLAR_IRRADIANCE_B5'] = gee_metadata['SOLAR_IRRADIANCE_B5']
    metadata['SOLAR_IRRADIANCE_B6'] = gee_metadata['SOLAR_IRRADIANCE_B6']
    metadata['SOLAR_IRRADIANCE_B7'] = gee_metadata['SOLAR_IRRADIANCE_B7']
    metadata['SOLAR_IRRADIANCE_B8A'] = gee_metadata['SOLAR_IRRADIANCE_B8A']
    metadata['SOLAR_IRRADIANCE_B11'] = gee_metadata['SOLAR_IRRADIANCE_B11']
    metadata['SOLAR_IRRADIANCE_B12'] = gee_metadata['SOLAR_IRRADIANCE_B12']

    return metadata
