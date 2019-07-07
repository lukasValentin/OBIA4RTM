#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  6 13:09:42 2019

@author: Lukas Graf, graflukas@web.de

This modul provides functions to extract the S2-metadata required for the
subsequent analysis steps in OBIA4RTM in an automated way.
The xml file must follow the structure provided by Sen2Core L2-Output.
"""
import numpy as np
from OBIA4RTM.mdata_proc.parse_s2xml import parse_s2xml


def run_xml_parser(path_to_xml):
    """
    calls parse_s2xml for reading in the metadata into a dictionary
    
    Parameters
    ----------
    path_to_xml : String
        Path and filename of the xml file containing the S2 metadata
    """
    metadata = parse_s2xml(path_to_xml)
    
    if metadata is None:
        print("Reading of Metadata from xml failed!")
    # endif
    
def get_mean_angles(sensor_data):
    """
    get mean sensor azimuth and zenith angles for further setup
    of RTM and proper metadata storage
    only deal with those bands that are used for the plant parameter retrieval
    
    Parameters
    ----------
    sensor_data : Dictionary
        Dictionary holding the metadata extracted from the S2-metadata xml
    
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
    
    return m_sensor_azimuth, m_sensor_zenith, m_rel_azimuth