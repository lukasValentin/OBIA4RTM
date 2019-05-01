# -*- coding: utf-8 -*-
import os, sys
import numpy as np
from osgeo import ogr, osr, gdal
import psycopg2


def get_mean_refl(shp_file, raster_file, num_bands, acqui_date, conn, cursor, table_name):
    """
    calculates mean reflectance per object in image
    """
    
    # iterate over the shapefile to get the metadata
    # Shapefile handling
    driver = ogr.GetDriverByName('ESRI Shapefile')
    shpfile = driver.Open(shp_file)
    layer = shpfile.GetLayer(0)
    num_objects = layer.GetFeatureCount()
    
    print(str(num_objects) + " image objects will be processed. This might take a while...") 
    
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
    epsg = int(proj.GetAttrValue('AUTHORITY',1))
    
    # check the image raster
    if (raster.RasterCount != num_bands):
        print("ERROR: The number of bands you provided does not match the image file!")

    # Get geometry and extent of feature 
    for ii in range(num_objects):
        
        feature = layer.GetFeature(ii)
        geom = feature.GetGeometryRef()
        # get well-known-text of feature geomtry
        wkt = geom.ExportToWkt()  
        f_id = feature.GetFID()
        luc = feature.GetField(acqui_date)
        
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
            zoneraster = np.ma.masked_array(dataraster,  np.logical_not(datamask))
            mean = np.nanmean(zoneraster) * 0.01
            meanValues.append(mean)
        
            index += 1
        #endfor
                
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
        try:
            cursor.execute(query)
            conn.commit()
            
        except (psycopg2.DatabaseError, Exception) as err:
            print("Could not insert image object with ID " + str(f_id) + " into table " + table_name)
            print(err)
            #conn.rollback()
            continue
    #endfor
    
    # close the GDAL-bindings to the files
    raster = None
    shpfile = None
    layer = None
    
# end
