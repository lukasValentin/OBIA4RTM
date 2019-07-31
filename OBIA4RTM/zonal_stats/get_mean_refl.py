#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 10:34:57 2019

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
import sys
import numpy as np
from osgeo import ogr, osr, gdal
from psycopg2 import DatabaseError, ProgrammingError
from OBIA4RTM.configurations.logger import close_logger


def get_mean_refl(shp_file, raster_file, acqui_date, conn, cursor,
                  table_name, logger):
    """
    calculates mean reflectance per object in image. Uses GDAL-Python bindings
    for reading the shape and raster data.

    Parameters
    ----------
    shp_file : String
        file-path to ESRI shapefile with the image object boundaries
    raster_file : String
        file-path to raster containing Sentinel-2 imagery as GeoTiff
        it is assumed that clouds/ shadows etc have already been masked out
        and these pixels are set to the according NoData value
    acqui_date : String
        acquisition date of the imagery (used for linking to LUT and metadata)
    conn : psycopg2 Database connection
        connection to OBIA4RTM database
    cursor : psycopg2 database cursor
        for querying, updating and inserting into the OBIA4RTM database
    table_name : String
        Name of the table the object reflectance values should be written to
    logger : logging Logger object
        for tracking the progress and errors

    Returns
    -------
    None
    """
    # iterate over the shapefile to get the metadata
    # Shapefile handling
    driver = ogr.GetDriverByName('ESRI Shapefile')
    shpfile = driver.Open(shp_file)
    layer = shpfile.GetLayer(0)
    num_objects = layer.GetFeatureCount()

    logger.info("{0} image objects will be processed. This might take a while...".format(
            num_objects))

    # loop over single features
    # get geometry of features and their ID as well as mean reflectane per band
    
    # open raster data value
    raster = gdal.Open(raster_file)

    # Get image raster georeference info
    transform = raster.GetGeoTransform()
    xOrigin = transform[0]
    yOrigin = transform[3]
    pixelWidth = transform[1]
    pixelHeight = transform[5]
    
    # extract the epsg-code
    proj = osr.SpatialReference(wkt=raster.GetProjection())
    epsg = int(proj.GetAttrValue('AUTHORITY', 1))
    # check with the epsg of the shapefile
    ref = layer.GetSpatialRef()
    if ref is None:
        logger.warning('The layer has no projection info! Assume it is the same'\
                       'as for the imagery - but check results!')
        shp_epsg = epsg
    else:
        code = ref.GetAuthorityCode(None)
        shp_epsg = int(code)

    # check if the raster and the shapefile epsg match
    if epsg != shp_epsg:
        logger.error('The projection of the imagery does not match the projection '\
                     'of the shapefile you provided!'\
                     'EPSG-Code of the Image: EPSG:{0}; '\
                     'EPSG-Code of the Shapefile: EPSG:{1}'.format(
                             epsg,
                             shp_epsg))
        close_logger(logger)
        sys.exit('An error occured while execute get_mean_refl. Check logfile!')
    
    # check the image raster
    num_bands = 9 # Sentinel-2 bands: B2, B3, B4, B5, B6, B7, B8A, B11, B12
    if (raster.RasterCount != num_bands):
        logger.error("The number of bands you provided does not match the image file!")
        close_logger(logger)
        sys.exit(-1)

    # determine the min area of an object (determined by S2 spatial resolution)
    # use the "standard" resolution of 20 meters
    # an object must be twice times larger
    min_area = 20 * 60 * 2

    # for requesting the landuse information
    luc_field = 'LU' + acqui_date.replace('-', '')
    # Get geometry and extent of feature 
    for ii in range(num_objects):
        feature = layer.GetFeature(ii)
        # extract the geometry
        geom = feature.GetGeometryRef()
        # get well-known-text of feature geomtry
        wkt = geom.ExportToWkt()
        # extract feature ID
        f_id = feature.GetFID()
        # get the area of the current feature
        area = geom.Area()  # m2
        # the area must be at least 2.5 times larger than the coarsest
        # possible spatial resolution of Sentinel-2 (60 by 60 meters)
        if area < min_area:
            logger.warning('The object {0} was too small compared to the '\
                           'spatial resolution of Sentinel-2! '\
                           'Object area (m2): {1}; Minimum area required (m2): '\
                           '{2} -> skipping'.format(
                                   f_id,
                                   area,
                                   min_area))
            continue
        luc = feature.GetField(luc_field)

        # convert to integer coding if luc is provided as text
        try:
            luc = int(luc)
        except ValueError:
            luc = luc.upper()
            query = "SELECT landuse FROM s2_landuse WHERE landuse_semantic = '{0}';".format(
                    luc)
            cursor.execute(query)
            res = cursor.fetchall()
            luc = int(res[0][0])
        # end try-except

        # check for feature type -> could be either POLYGON or MULTIPOLYGON
        if (geom.GetGeometryName() == 'MULTIPOLYGON'):
            count = 0
            pointsX = []; pointsY = []
            for polygon in geom:
                geomInner = geom.GetGeometryRef(count)
                ring = geomInner.GetGeometryRef(0)
                numpoints = ring.GetPointCount()
                for p in range(numpoints):
                    lon, lat, z = ring.GetPoint(p)
                    pointsX.append(lon)
                    pointsY.append(lat)
            count += 1
        elif (geom.GetGeometryName() == 'POLYGON'):
            ring = geom.GetGeometryRef(0)
            numpoints = ring.GetPointCount()
            pointsX = []; pointsY = []; values = [];
            for p in range(numpoints):
                lon, lat, val = ring.GetPoint(p)
                pointsX.append(lon)
                pointsY.append(lat)
                values.append(val)

        else:
            sys.exit("ERROR: Geometry needs to be either Polygon or Multipolygon")
        #endif
        
        #get exact extent of feature for masking
        xmin = min(pointsX)
        xmax = max(pointsX)
        ymin = min(pointsY)
        ymax = max(pointsY)

        # Specify offset and rows and columns to read 
        # -> thus, only a part of the array must be read
        # -> calculate the offset in rows in cols to go the specific part of the S2-raster
        xoff = int((xmin - xOrigin)/pixelWidth)
        yoff = int((yOrigin - ymax)/pixelWidth)
        xcount = int((xmax - xmin)/pixelWidth)+1
        ycount = int((ymax - ymin)/pixelWidth)+1
        
        # temporary raster for masking the actual feature
        target_ds = gdal.GetDriverByName('MEM').Create('', xcount, ycount, 1, gdal.GDT_Byte)
        target_ds.SetGeoTransform((
                xmin, pixelWidth, 0,
                ymax, 0, pixelHeight,
                ))
        
        # Rasterize zone polygon to raster
        gdal.RasterizeLayer(target_ds, [1], layer, burn_values=[1])

        # the mask to be used for the calculation of the stats
        bandmask = target_ds.GetRasterBand(1)
        datamask = bandmask.ReadAsArray(0, 0, xcount, ycount).astype(np.float)

        # Rasterize zone polygon to raster -> thus data is only read at the location of the
        #actual feature
        gdal.RasterizeLayer(target_ds, [1], layer, burn_values=[1])
        
        # Read image raster as array
        meanValues = []
        # iterator variable for looping over Sentinel-2 bands
        index = 1
        for ii in range(raster.RasterCount):
        
            banddataraster = raster.GetRasterBand(index)
            # read image data at the specific extent covering the actual feature
            dataraster = banddataraster.ReadAsArray(xoff, yoff, xcount, ycount).astype(np.float)

            # Mask zone of raster
            zoneraster = np.ma.masked_array(dataraster, np.logical_not(datamask))
            # apply conversion factor of 0.01 to get the correct reflectance
            # values for ProSAIL
            mean = np.nanmean(zoneraster) * 0.01
            meanValues.append(mean)
            # increment index
            index += 1
        #endfor
        # check if the results are not nan -> if there are nans skip the object
        # as the ProSAIL model inversion cannot deal with missing values
        if any(np.isnan(meanValues)):
            logger.warning('The object with ID {} contains NaNs -> skipping!')
            continue

        #insert the mean reflectane and the object geometry into DB
        query = "INSERT INTO {0} (object_id, acquisition_date, landuse, object_geom, " \
                "b2, b3, b4, b5, b6, b7, b8a, b11, b12) VALUES ( " \
                "{1}, '{2}', {3}, ST_Multi(ST_GeometryFromText('{4}', {5})), " \
                "{6}, {7}, {8}, {9}, {10}, {11}, {12}, {13}, {14});".format(
                        table_name,
                        f_id,
                        acqui_date,
                        luc,
                        wkt,
                        epsg,
                        np.round(meanValues[0], 4),
                        np.round(meanValues[1], 4),
                        np.round(meanValues[2], 4),
                        np.round(meanValues[3], 4),
                        np.round(meanValues[4], 4),
                        np.round(meanValues[5], 4),
                        np.round(meanValues[6], 4),
                        np.round(meanValues[7], 4),
                        np.round(meanValues[8], 4),
                        )
        # catch errors for single objects accordingly and continue with next
        # object to avoid interrupts of whole workflow
        try:
            cursor.execute(query)
            conn.commit()
        except (DatabaseError, ProgrammingError):
            logger.error("Could not insert image object with ID {0} into table '{1}'".format(
                    f_id, table_name), exc_info=True)
            conn.rollback()
            continue
    #endfor

    # close the GDAL-bindings to the files
    raster = None
    shpfile = None
    layer = None
    
# end
