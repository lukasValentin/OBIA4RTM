#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 10:58:16 2019

@author: lukas
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
        
    except (Exception) as err:
        
        print("Could not retrieve sensor metatdata!")
        print(err)
        
    # endif
    
    return centers, fwhm
# end get_s2band


def get_resampler(conn, cursor, sensor):
    """
    get the spectral properties of a sensor and generate a resampler object
    """
    # get S2 sensor-response function
    centers, fwhm = get_bands(conn, cursor, sensor)
        
    # define centers and bandwith of prosail output
    centers_prosail = np.arange(400,2501,1)
    fwhm_prosail = np.ones(centers_prosail.size)
    
    resampler = BandResampler(centers_prosail, centers, fwhm1=fwhm_prosail, fwhm2=fwhm)
    return resampler
# end get_resampler
    