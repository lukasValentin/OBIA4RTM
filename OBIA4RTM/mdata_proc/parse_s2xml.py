#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 13:54:35 2019

This module is part of OBIA4RTM.

Copyright (c) 2019 Lukas Graf

@author: Lukas Graf, graflukas@web.de
"""
from xml.dom import minidom


def parse_s2xml(xml_file):
    """
    Parses S2 xml file and extractes the metadata into a dictionary
    derived from Sen2Core Atmospheric Correction

    Parameters
    ----------
    xml_file : String
        Filename (incl. file path) of the scene metadata xml

    Returns
    -------
    metadata : Dictionary
        Dictionary containing the most relevant scene metadata (geometries, SRS, preclass, ...)
    """
    # parse the xml file into a minidom object
    xmldoc = minidom.parse(xml_file)
    
    # now, the values of some relevant tags can be extracted:
    metadata = dict()
    
    # tile id -> scene_id
    # if condition to account for changes in metadata xml
    tile_id_xml = xmldoc.getElementsByTagName('TILE_ID_2A')
    if tile_id_xml == []:
        tile_id_xml = xmldoc.getElementsByTagName('TILE_ID')
    tile_id = tile_id_xml[0].firstChild.nodeValue
    scene_id = tile_id.split(".")[0]
    metadata['SCENE_ID'] = scene_id
    # Sensor
    sensor = scene_id[0:3]
    metadata['SENSOR'] = sensor

    # sensing time (acquisition time)
    sensing_time_xml = xmldoc.getElementsByTagName('SENSING_TIME')
    sensing_time = sensing_time_xml[0].firstChild.nodeValue
    metadata['SENSING_TIME'] = sensing_time

    # number of rows and columns for each resolution -> 10, 20, 60 meters
    nrows_xml = xmldoc.getElementsByTagName('NROWS')
    ncols_xml = xmldoc.getElementsByTagName('NCOLS')
    resolutions = ['_10m', '_20m', '_60m']
    # order: 10, 20, 60 meters spatial resolution
    for ii in range(3):
        nrows = nrows_xml[ii].firstChild.nodeValue
        ncols = ncols_xml[ii].firstChild.nodeValue
        metadata['NROWS' + resolutions[ii]] = nrows
        metadata['NCOLS' + resolutions[ii]] = ncols
    # endfor

    # EPSG-code
    epsg_xml = xmldoc.getElementsByTagName('HORIZONTAL_CS_CODE')
    epsg = epsg_xml[0].firstChild.nodeValue
    metadata['EPSG'] = epsg

    # Upper Left Corner coordinates -> again for all resolutions
    ulx_xml = xmldoc.getElementsByTagName('ULX')
    uly_xml = xmldoc.getElementsByTagName('ULY')
    # order: 10, 20, 60 meters spatial resolution
    for ii in range(3):
        ulx = ulx_xml[ii].firstChild.nodeValue
        uly = uly_xml[ii].firstChild.nodeValue
        metadata['ULX' + resolutions[ii]] = ulx
        metadata['ULY' + resolutions[ii]] = uly
    # endfor

    # extract the mean zenith and azimuth angles
    zenith_xml = xmldoc.getElementsByTagName('ZENITH_ANGLE')
    azimuth_xml = xmldoc.getElementsByTagName('AZIMUTH_ANGLE')
    # first, the sun angles are given followed by the individiual bands (observer)
    order = ['_SUN', '_0', '_1', '_10', '_1', '_2', '_3', '_4', '_5', '_6', '_7', '_8', '_11', '_12']
    for ii in range(14):
        zenith = zenith_xml[ii].firstChild.nodeValue
        azimuth = azimuth_xml[ii].firstChild.nodeValue
        metadata['ZENITH' + order[ii]] = zenith
        metadata['AZIMUTH' + order[ii]] = azimuth
    # endfor

    # extract scene relevant data about nodata values, cloud coverage, luc etc.
    # Level 1C content
    cloudy_xml = xmldoc.getElementsByTagName('CLOUDY_PIXEL_PERCENTAGE')
    cloudy = cloudy_xml[0].firstChild.nodeValue
    metadata['CLOUDY_PIXEL_PERCENTAGE'] = cloudy

    degraded_xml = xmldoc.getElementsByTagName('DEGRADED_MSI_DATA_PERCENTAGE')
    degraded = degraded_xml[0].firstChild.nodeValue
    metadata['DEGRADED_MSI_DATA_PERCENTAGE'] = degraded

    # Level 2A content
    nodata_xml = xmldoc.getElementsByTagName('NODATA_PIXEL_PERCENTAGE')
    nodata = nodata_xml[0].firstChild.nodeValue
    metadata['NODATA_PIXEL_PERCENTAGE'] = nodata

    darkfeatures_xml = xmldoc.getElementsByTagName('DARK_FEATURES_PERCENTAGE')
    darkfeatures = darkfeatures_xml[0].firstChild.nodeValue
    metadata['DARK_FEATURES_PERCENTAGE'] = darkfeatures

    cs_xml = xmldoc.getElementsByTagName('CLOUD_SHADOW_PERCENTAGE')
    cs = cs_xml[0].firstChild.nodeValue
    metadata['CLOUD_SHADOW_PERCENTAGE'] = cs

    veg_xml = xmldoc.getElementsByTagName('VEGETATION_PERCENTAGE')
    veg = veg_xml[0].firstChild.nodeValue
    metadata['VEGETATION_PERCENTAGE'] = veg

    noveg_xml = xmldoc.getElementsByTagName('NOT_VEGETATED_PERCENTAGE')
    noveg = noveg_xml[0].firstChild.nodeValue
    metadata['NOT_VEGETATED_PERCENTAGE'] = noveg

    water_xml = xmldoc.getElementsByTagName('WATER_PERCENTAGE')
    water = water_xml[0].firstChild.nodeValue
    metadata['WATER_PERCENTAGE'] = water

    unclass_xml = xmldoc.getElementsByTagName('UNCLASSIFIED_PERCENTAGE')
    unclass = unclass_xml[0].firstChild.nodeValue
    metadata['UNCLASSIFIED_PERCENTAGE'] = unclass

    cproba_xml = xmldoc.getElementsByTagName('MEDIUM_PROBA_CLOUDS_PERCENTAGE')
    cproba = cproba_xml[0].firstChild.nodeValue
    metadata['MEDIUM_PROBA_CLOUDS_PERCENTAGE'] = cproba

    hcproba_xml = xmldoc.getElementsByTagName('HIGH_PROBA_CLOUDS_PERCENTAGE')
    hcproba = hcproba_xml[0].firstChild.nodeValue
    metadata['HIGH_PROBA_CLOUDS_PERCENTAGE'] = hcproba

    thcirrus_xml = xmldoc.getElementsByTagName('THIN_CIRRUS_PERCENTAGE')
    thcirrus = thcirrus_xml[0].firstChild.nodeValue
    metadata['THIN_CIRRUS_PERCENTAGE'] = thcirrus
    
    # try catch because of version differences in xml file
    try:
        ccover_xml = xmldoc.getElementsByTagName('CLOUD_COVERAGE_PERCENTAGE')
        ccover = ccover_xml[0].firstChild.nodeValue
        metadata['CLOUD_COVERAGE_PERCENTAGE'] = ccover
    except IndexError:
        pass

    snowice_xml = xmldoc.getElementsByTagName('SNOW_ICE_PERCENTAGE')
    snowice = snowice_xml[0].firstChild.nodeValue
    metadata['SNOW_ICE_PERCENTAGE'] = snowice

    return metadata
