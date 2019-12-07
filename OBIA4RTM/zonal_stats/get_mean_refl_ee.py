#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 08:29:42 2019

This module is part of OBIA4RTM. It is part of the optional Google-Earth-Engine
extension and extends the file-based get_mean_refl.py script to an according
GEE version.

Copyright (c) 2019 Lukas Graf

@author: Lukas Graf, graflukas@web.de
"""
import sys
import ast
import numpy as np
import ee
from osgeo import ogr, osr
from psycopg2 import DatabaseError, ProgrammingError
from OBIA4RTM.configurations.connect_db import connect_db, close_db_connection
from OBIA4RTM.configurations.logger import get_logger, close_logger


def transform_utm_to_wgs84(easting, northing, zone):
    """
    converts UTM easting, northing to lon, lat
    found on: 
    https://stackoverflow.com/questions/343865/how-to-convert-from-utm-to-latlng-in-python-or-javascript

    Parameters
    ----------
    easting : Float
        UTM-Easting (m)
    northing : Float
        UTM-Northing (m)
    zone : Integer
        UTM-Zone number

    Returns
    -------
    lon : Float
        Longitude (deg)
    lat : Float
        Latitude (deg)
    alt : Float
        Altitude (m)
    """
    utm_coordinate_system = osr.SpatialReference()
    # Set geographic coordinate system to handle lat/lon
    utm_coordinate_system.SetWellKnownGeogCS("WGS84")
    # check hemisphere
    is_northern = northing > 0
    utm_coordinate_system.SetUTM(zone, is_northern)
    # Clone ONLY the geographic coordinate system
    wgs84_coordinate_system = utm_coordinate_system.CloneGeogCS() 
    # create transform component
    utm_to_wgs84_transform = osr.CoordinateTransformation(utm_coordinate_system,
                                                          wgs84_coordinate_system)
    # returns lon, lat, altitude
    return utm_to_wgs84_transform.TransformPoint(easting, northing, 0)


def get_mean_refl_ee(shp_file, img, acqui_date, scene_id, table_name):
    """
    calculates mean reflectance per object in image. Uses GEE-Python bindings
    for reading the shape and Sentinel-2 imagery data.

    Parameters
    ----------
    shp_file : String
        file-path to ESRI shapefile with the image object boundaries
    img : ee.image.Image
        GEE imagery containing the atmospherically collected Sentinel-2 data
    acqui_date : String
        acquisition date of the imagery (used for linking to LUT and metadata)
    scene_id : String
        ID of the Sentinel-2 scene
    table_name : String
        Name of the table the object reflectance values should be written to

    Returns
    -------
    None
    """
    # open the database connection to OBIA4RTM's backend
    conn, cursor = connect_db()
    # get a logger
    logger = get_logger()
    # in case it isn't done yet:
    ee.Initialize()
    
    # iterate over the shapefile to get the metadata
    # Shapefile handling
    driver = ogr.GetDriverByName('ESRI Shapefile')
    shpfile = driver.Open(shp_file)
    # check if shapefile exists and could be opened
    if shpfile is None:
        raise TypeError("The provided File '{}' is invalid or blocked!".format(
                shp_file))
    layer = shpfile.GetLayer(0)
    num_objects = layer.GetFeatureCount()

    logger.info("{0} image objects will be processed. This might take a while...".format(
            num_objects))
    
    # loop over single features
    # get geometry of features and their ID as well as mean reflectane per band

    # before that check the raster metadata from GEE
    img_epsg = img.select('B2').projection().crs().getInfo()
    img_epsg = int(img_epsg.split(':')[1])
    # check with the epsg of the shapefile
    ref = layer.GetSpatialRef()
    if ref is None:
        logger.warning('The layer has no projection info! Assume it is the same'\
                       'as for the imagery - but check results!')
        shp_epsg = img_epsg
        # asuming that the imagery is projected in UTM as it should
        # the UTM-Zone is stored in the last two digits
        utm = int(str(shp_epsg)[3::])
    else:
        code = ref.GetAuthorityCode(None)
        shp_epsg = int(code)
        utm = ref.GetUTMZone()

    if img_epsg != shp_epsg:
        logger.error('The projection of the imagery does not match the projection '\
                     'of the shapefile you provided!'\
                     'EPSG-Code of the Image: EPSG:{0}; '\
                     'EPSG-Code of the Shapefile: EPSG:{1}'.format(
                             img_epsg,
                             shp_epsg))
        close_logger(logger)
        sys.exit('An error occured while execute get_mean_refl. Check logfile!')
    # determine the min area of an object (determined by S2 spatial resolution)
    # use the "standard" resolution of 20 meters
    # an object must be twice times larger
    min_area = 20 * 60 * 2

    # for requesting the landuse information
    luc_field = 'LU' + acqui_date.replace('-', '')
    # start iterating over features
    # Get geometry and extent of feature 
    for ii in range(num_objects):
        feature = layer.GetFeature(ii)
        # extract the geometry
        geom = feature.GetGeometryRef()
        # get a well-know text representation -> required by PostGIS
        wkt = geom.ExportToWkt()
        # get the ID
        # f_id = feature.GetFID() # depraceted
        f_id = feature.GetField('id')
        # get the land cover code
        luc = feature.GetField(luc_field)
        # convert to integer coding if luc is provided as text
        try:
            luc = int(luc)
        except ValueError:
            luc = luc.upper()
            query = "SELECT landuse FROM public.s2_landuse WHERE landuse_semantic = "\
            "'{0}';".format(
                    luc)
            cursor.execute(query)
            res = cursor.fetchall()
            luc = int(res[0][0])
        # end try-except
        # get the area of the feature and check if it fits the image
        # resolution -> if the object is to small skip it
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

        # export the coordinates of the geometry temporarily to JSON dictionary
        # for communicating with GEE
        geom_json = ast.literal_eval(geom.ExportToJson())
        # get the geometry type
        # allowed values: Polygon and Multipolygon
        geom_type = geom_json.get('type')
        # get the coordinates
        geom_coords = geom_json.get('coordinates')[0]
        # must be converted to lon, lat for GEE
        geo_coords = []
        for geom_coord in geom_coords:
            easting = geom_coord[0]
            northing = geom_coord[1]
            # call transform method
            lon, lat, alt = transform_utm_to_wgs84(easting,
                                                   northing,
                                                   utm)
            geo_coord = []
            geo_coord.append(lon)
            geo_coord.append(lat)
            geo_coords.append(geo_coord)

        if geom_type not in ['Polygon', 'Multipolygon']:
            logger.warning('Object with ID {} is not of type Polygon or '\
                           'Multipolygon -> skipping'.format(f_id))
            continue
        # construct a GEE geometry
        # TODO -> test what happens for Multipolygon!
        geom_gee = ee.geometry.Geometry.Polygon(geo_coords)

        # use the image reduce function to get the mean reflectance values
        # for each of the nine bands used in GEE
        meanDictionary = img.reduceRegion(
                reducer = ee.Reducer.mean(),
                geometry = geom_gee
                )

        # extract the computed mean values for the particular image
        # only use those bands required for OBIA4RTM
        # multiply with 100 to get % surface reflectance values
        multiplier = 100
        # surround with try-except in case only blackfill was found for a object
        try:
            B2 = meanDictionary.get('B2').getInfo() * multiplier
            B3 = meanDictionary.get('B3').getInfo() * multiplier
            B4 = meanDictionary.get('B4').getInfo() * multiplier
            B5 = meanDictionary.get('B5').getInfo() * multiplier
            B6 = meanDictionary.get('B6').getInfo() * multiplier
            B7 = meanDictionary.get('B7').getInfo() * multiplier
            B8A = meanDictionary.get('B8A').getInfo() * multiplier
            B11 = meanDictionary.get('B11').getInfo() * multiplier
            B12 = meanDictionary.get('B12').getInfo() * multiplier
        except TypeError:
            logger.info('No spectral information found for Object with ID {}'.format(
                    f_id))
            continue
        # check cloud and shadow mask
        # the cloud and shadow masks are binary
        # if the average is zero everything is OK (=no clouds, no shadows)
        cm = meanDictionary.get('CloudMask').getInfo()
        sm = meanDictionary.get('ShadowMask').getInfo()
        # if the shadow and/ or the cloud mask is not zero on average
        # -> skip the object as it is cloud covered or affected by
        # cloud shadows
        if cm > 0:
            logger.info('Object with ID {} is coverd by clouds -> skipping'.format(
                    f_id))
            continue
        if sm > 0:
            logger.info('Object with ID {} is coverd by cloud shadows -> skipping'.format(
                    f_id))
            continue
        # also make sure that the object really contains reflectance values
        # checking the first band should be sufficient
        if B2 is None:
            logger.info('Object with ID {} contains only NaN values -> skipping'.format(
                    f_id))
            continue
        # otherwise insert the data into the PostgreSQL database
        try:
            query = "INSERT INTO {0} (object_id, acquisition_date, landuse, object_geom, "\
                    "b2, b3, b4, b5, b6, b7, b8a, b11, b12, scene_id) VALUES ( " \
                    "{1}, '{2}', {3}, ST_Multi(ST_GeometryFromText('{4}', {5})), " \
                    "{6}, {7}, {8}, {9}, {10}, {11}, {12}, {13}, {14}, '{15}') "\
                    " ON CONFLICT (object_id, scene_id) DO NOTHING;".format(
                            table_name,
                            f_id,
                            acqui_date,
                            luc,
                            wkt,
                            img_epsg,
                            np.round(B2, 4),
                            np.round(B3, 4),
                            np.round(B4, 4),
                            np.round(B5, 4),
                            np.round(B6, 4),
                            np.round(B7, 4),
                            np.round(B8A, 4),
                            np.round(B11, 4),
                            np.round(B12, 4),
                            scene_id
                            )
        except ValueError:
            logger.error("Invalid string syntax encountered when attempting"\
                         " to generate INSERT for field {0} on '{1}'".format(
                                     f_id, acqui_date))
            continue
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
    shpfile = None
    layer = None
    # close database connection
    close_db_connection(conn, cursor)
    # close the logger
    close_logger(logger)
