#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 28 10:18:46 2019

This module is part of OBIA4RTM (GEE extension) with many parts taken directly
from https://github.com/samsammurphy/cloud-masking-sentinel2/blob/master/cloud-masking-sentinel2.ipynb
(available under Apache 2.0 license)

Slight changes were applied to translate the original code provided as Jupyter
Notebook into the OBIA4RTM architecture. Functionalities were not altered.

Copyright (c) 2019 Lukas Graf, Sam Murphy


                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/
"""
import math
import ee


def rescale(img, thresholds):
    """
    Linear stretch of image between two threshold values.
    Taken from
    https://github.com/samsammurphy/cloud-masking-sentinel2/blob/master/cloud-masking-sentinel2.ipynb
    Availabe under Apache 2.0 licence

    Parameters
    ----------
    img : gee.image.Image
        Image the stretch should be apploed two
    thresholds : List
        list with two elemts specifying upper and lower bound for stretching

    Returns
    -------
    img : gee.image.Image
        stretched image
    """
    return img.subtract(thresholds[0]).divide(thresholds[1] - thresholds[0])


def sentinelCloudScore(img):
    """
    Computes spectral indices of cloudyness and takes the minimum of them.
    
    Each spectral index is fairly lenient because the group minimum 
    is a somewhat stringent comparison policy.
    side note -> this seems like a job for machine learning :)
    
    originally written by Matt Hancher for Landsat imagery
    adapted to Sentinel by Chris Hewig and Ian Housman

    Parameters
    ----------
    img : gee.image.Image
        Sentinel-2 Image for which the cloud mask should be calculated

    Returns
    -------
    img : gee.image.Image
        Sentinel-2 image with cloud score as extra band
    """
    # cloud until proven otherwise
    score = ee.Image(1)
    # clouds are reasonably bright
    score = score.min(rescale(img.select(['blue']), [0.1, 0.5]))
    score = score.min(rescale(img.select(['aerosol']), [0.1, 0.3]))
    score = score.min(rescale(img.select(['aerosol']).add(img.select(['cirrus'])), [0.15, 0.2]))
    score = score.min(rescale(img.select(['red']).add(img.select(['green'])).add(img.select('blue')), [0.2, 0.8]))
    # clouds are moist
    ndmi = img.normalizedDifference(['red4','swir1'])
    score=score.min(rescale(ndmi, [-0.1, 0.1]))
    # clouds are not snow (use Normalized Differential Snow Index)
    ndsi = img.normalizedDifference(['green', 'swir1'])
    score=score.min(rescale(ndsi, [0.8, 0.6])).rename(['cloudScore'])
    return img.addBands(score)


def ESAcloudMask(img):
    """
    European Space Agency (ESA) clouds from 'QA60', i.e. Quality Assessment band at 60m

    parsed by Nick Clinton

    Parameters
    ----------
    img : gee.image.Image
        Sentinel-2 Image for which the cloud mask should be calculated

    Returns
    -------
    img : gee.image.Image
        Sentinel-2 image with cloud score as extra band
    """
    qa = img.select('QA60')
    # bits 10 and 11 are clouds and cirrus
    cloudBitMask = int(2**10)
    cirrusBitMask = int(2**11)
    # both flags set to zero indicates clear conditions.
    clear = qa.bitwiseAnd(cloudBitMask).eq(0).And(\
           qa.bitwiseAnd(cirrusBitMask).eq(0))
    # clouds is not clear
    cloud = clear.Not().rename(['ESA_clouds'])
    # return the masked and scaled data.
    return img.addBands(cloud)


def shadowMask(img, cloudMaskType):
    """
    Finds cloud shadows in images
    Originally by Gennadii Donchyts, adapted by Ian Housman
    NOTE: the cloud mask must have been computed and added as separate
    band to the Sentinel-2 imagery
    """
    # auxiliary function
    def _potentialShadow(cloudHeight):
        """
        Finds potential shadow areas from array of cloud heights
        
        returns an image stack (i.e. list of images) 
        """
        cloudHeight = ee.Number(cloudHeight)
        
        # shadow vector length
        shadowVector = zenith.tan().multiply(cloudHeight)
        
        # x and y components of shadow vector length
        x = azimuth.cos().multiply(shadowVector).divide(nominalScale).round()
        y = azimuth.sin().multiply(shadowVector).divide(nominalScale).round()
        
        # affine translation of clouds
        cloudShift = cloudMask.changeProj(cloudMask.projection(), cloudMask.projection().translate(x, y)) # could incorporate shadow stretch?
        
        return cloudShift
  
    # select a cloud mask
    cloudMask = img.select(cloudMaskType)
    
    # make sure it is binary (i.e. apply threshold to cloud score)
    cloudScoreThreshold = 0.5
    cloudMask = cloudMask.gt(cloudScoreThreshold)

    # solar geometry (radians)
    azimuth = ee.Number(img.get('solar_azimuth')).multiply(math.pi).divide(180.0).add(ee.Number(0.5).multiply(math.pi))
    zenith  = ee.Number(0.5).multiply(math.pi ).subtract(ee.Number(img.get('solar_zenith')).multiply(math.pi).divide(180.0))

    # find potential shadow areas based on cloud and solar geometry
    nominalScale = cloudMask.projection().nominalScale()
    cloudHeights = ee.List.sequence(500,4000,500)        
    potentialShadowStack = cloudHeights.map(_potentialShadow)
    potentialShadow = ee.ImageCollection.fromImages(potentialShadowStack).max()

    # shadows are not clouds
    potentialShadow = potentialShadow.And(cloudMask.Not())

    # (modified) dark pixel detection 
    darkPixels = img.normalizedDifference(['green', 'swir2']).gt(0.25)

    # shadows are dark
    shadows = potentialShadow.And(darkPixels).rename(['shadows'])
    
    # might be scope for one last check here. Dark surfaces (e.g. water, basalt, etc.) cause shadow commission errors.
    # perhaps using a NDWI (e.g. green and nir)
    return img.addBands(shadows)


def mask_clouds(s2_image, option):
    """
    this function masks out clouds from Sentinel-2 TOA imagery using the
    quality information provided by the ESA-internal pre-processing chain
    (Level 1C).
    Quality flag bits 10 and 11 (clouds and cirrus, respectively) are masked
    out. Of course, this is only a very rough cloud correction approach
    as shadowing effects are disregarded.
    Therefore, users might come up with a more sophisticated soluation for
    their own processing workflow

    Parameters
    ----------
    s2_image : ee.image.Image
        Sentinel-2 imagery (from GEE) to be masked for clouds and cirrus
    option : Integer
        two options (1 and 2) are available for cloud masking
        1 = use ESA quality information
        2 = use Matt Hancher for Landsat imagery adapted to Sentinel by 
        Chris Hewig and Ian Housman

    Returns
    -------
    s2_masked : ee.image.Image
        Sentinel-2 imagery with masked clouds and cirrus (if any)
    """
    ee.Initialize()
    # convert to top-of-atmosphere reflectance
    # top of atmosphere reflectance
    toa = s2_image.select(['B1','B2','B3','B4','B5','B6','B7','B8A','B9','B10', 'B11','B12'],\
                 ['aerosol','blue', 'green', 'red', 'B5', 'red2', 'B7', 'red4','h2o', 'cirrus','swir1', 'swir2'])\
                 .divide(10000).addBands(s2_image.select('QA60'))\
                 .set('solar_azimuth',s2_image.get('MEAN_SOLAR_AZIMUTH_ANGLE'))\
                 .set('solar_zenith',s2_image.get('MEAN_SOLAR_ZENITH_ANGLE'))
    # which option should be used for the cloud masking
    # clouds and cloud shadows

    if option == 1:
        toa = ESAcloudMask(toa)
        toa = shadowMask(toa,'ESA_clouds')
        # reformat the output
        toa = toa.select(
            ['aerosol','blue', 'green', 'red', 'B5', 'red2', 'B7', 'red4','h2o', 'cirrus','swir1', 'swir2','ESA_clouds', 'shadows'],
    ['B1','B2','B3','B4','B5','B6','B7','B8A','B9','B10', 'B11','B12','CloudMask','ShadowMask'])
    elif option == 2:
        toa = sentinelCloudScore(toa)
        toa = shadowMask(toa,'cloudScore')
        toa = toa.select(
            ['aerosol','blue', 'green', 'red', 'B5', 'red2', 'B7', 'red4','h2o', 'cirrus','swir1', 'swir2', 'cloudScore', 'shadows'],
    ['B1','B2','B3','B4','B5','B6','B7','B8A','B9','B10', 'B11','B12','CloudMask','ShadowMask'])
    else:
        raise NotImplemented

    return toa
