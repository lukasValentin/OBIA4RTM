#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 11:17:10 2019

This module is part of OBIA4RTM.

Copyright (c) 2019 Lukas Graf

@author: Lukas Graf, graflukas@web.de
"""
import os
import sys
import json
from psycopg2 import DatabaseError
from OBIA4RTM.configurations.connect_db import connect_db, close_db_connection
from OBIA4RTM.mdata_proc.get_scene_metadata import get_mean_angles
from OBIA4RTM.mdata_proc.get_scene_metadata import get_sun_zenith_angle
from OBIA4RTM.mdata_proc.get_scene_metadata import get_sensor_and_sceneid
from OBIA4RTM.mdata_proc.get_scene_metadata import get_scene_footprint
from OBIA4RTM.mdata_proc.get_scene_metadata import get_acqusition_time


def insert_scene_metadata(metadata, use_gee, raster=None):
        """
        inserts the most important scene metadata before starting the inversion
        procedure into the OBIA4RTM PostgreSQL database

        Parameters
        ----------
        metadata : Dictionary
            Sentinel-2 scene metadata
        use_gee : Boolean
            true if GEE was used, false if Sen2Core was used
        raster : String
            File-path to the Sentinel-2 imagery in case Sen2core was used

        Returns
        -------
        None
        """
        # open database connection
        conn, cursor = connect_db()
        # get sensor and scene_id
        sensor, scene_id = get_sensor_and_sceneid(metadata)
        # get mean angles from scene-metadata
        # tto -> sensor zenith angle
        # psi -> relative azimuth angle between sensor and sun
        tto, psi = get_mean_angles(metadata)
        # sun zenith angle
        tts = get_sun_zenith_angle(metadata)
        # get the footprint already as PostGIS insert statment
        footprint_statement = get_scene_footprint(metadata,
                                                  gee=use_gee)
        # full metadata as JSON
        metadata_json = json.dumps(metadata)
        # storage drive and filename of the image raster data
        # this part only applies to Sen2Core preprocessing
        if use_gee:
            storage_drive = 'NA: Google Earth Engine'
            filename = 'NA: Google Earth Engine'
        else:
            splitted = os.path.split(raster)
            storage_drive = splitted[0]
            filename = splitted[1]
        # get acquisition time and date
        acquisition_time, acquisition_date = get_acqusition_time(metadata)
        # insert this basic metadata direclty into the OBIA4RTM database before
        # continuing
        statement = "INSERT INTO public.scene_metadata (acquisition_time, "\
                    "scene_id, sun_zenith, "\
                    "obs_zenith, rel_azimuth, sensor, footprint, full_description, "\
                    "storage_drive, filename) VALUES ('{0}','{1}',{2},{3},{4},"\
                    "'{5}',{6},'{7}','{8}','{9}') ON CONFLICT (scene_id) "\
                    "DO NOTHING;".format(
                            acquisition_time,
                            scene_id,
                            tts,
                            tto,
                            psi,
                            sensor,
                            footprint_statement,
                            metadata_json,
                            storage_drive,
                            filename
                            )
        try:
            cursor.execute(statement)
            conn.commit()
        except DatabaseError:
            raise DatabaseError('Insert of metadata failed!')
            sys.exit()
        # close database connection
        close_db_connection(conn, cursor)
