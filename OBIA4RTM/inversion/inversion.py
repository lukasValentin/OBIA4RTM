#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 10:34:57 2019

@author: lukas
"""
import psycopg2
from configparser import ConfigParser
import os
import sys
import prosail
import numpy as np
import json

import lookup_table as lut
from handle_metadata import get_resampler
#import get_mean_refl


class inversion:
    """
    performs the inversion of a satellite scene
    """
    
    def __init__(self, sensor, scene_id, postgres_init="postgres.ini", path_to_config="config.txt"):
        
        self.path_to_config = path_to_config
        self.sensor = sensor
        self.scene_id = scene_id
        
        # setup the DB connection
        try:
            # read the connection parameters from config-file (see template postgres.ini)
            parser = ConfigParser()
            parser.read(postgres_init)
            # and store them in a string
            conn_str = "host='{}' dbname='{}' user='{}' password='{}'". format(
                    parser.get('POSTGRESQL', 'host'),
                    parser.get('POSTGRESQL', 'dbname'),
                    parser.get('POSTGRESQL', 'username'),
                    parser.get('POSTGRESQL', 'password')
                    )
            
            # open connection
            self.conn = psycopg2.connect(conn_str)
            self.cursor = self.conn.cursor()
            
        except (Exception, psycopg2.DatabaseError) as err:
            
            print ("ERROR: Unable to connect to the database")
            print (err)
            sys.exit(-1)
        
        # try to locate the PROSAIL config file
        if (not os.path.isfile(path_to_config)):
            
            print("ERROR: Unable to locate the config file for PROSAIL!")
            sys.exit(-1)
        
        # endif
    
    # end __init__
        
    def gen_lut(self, inv_table, luc, acqui_date):
        """
        Generates the lookup table and stores it in the DB
        """
        # firstly, create the LUT from the params config file
        param_lut = lut.lookup_table(self.path_to_config)
        param_lut.generate_param_lut()
        
        print("INFO: Start to generate ProSAIL-LUT with " + str(param_lut.lut_size) + " simulations")
        
        # basic setup
        # initial plant parameters
        
        # default soil-spectra
        try:
            soils = np.genfromtxt("soil_reflectance.txt")
        except Exception as ex:
            print("ERROR: Could not find soil spectra!")
            print(ex)
        
        # get S2 sensor-response function
        resampler = get_resampler(self.conn, self.cursor, self.sensor)
        
        # which params should be inverted
        list_of_params = ['n', 'cab', 'car', 'cbrown', 'cw', 'cm', 'lai',
                          'lidfa', 'lidfb', 'rsoil', 'psoil', 'hspot',
                          'tts', 'tto', 'psi', 'typelidf']
        
        params_inv = dict()
        for ii in range(param_lut.to_be_inv[0].shape[0]):
            params_inv[str(ii)] = list_of_params[param_lut.to_be_inv[0][ii]]
            
        # convert to json
        params_inv_json = json.dumps(params_inv)
        
        # write the metadata into the inversion_mapping table
        insert = "INSERT INTO inversion_mapping (acquisition_date, " \
                 "params_to_be_inverted, landuse, sensor, scene_id) " \
                 "VALUES('{0}', '{1}', {2}, '{3}', '{4}');".format(
                         acqui_date,
                         params_inv_json,
                         luc,
                         self.sensor,
                         self.scene_id)
        
        try:
            self.cursor.execute(insert)
            self.conn.commit()
        except (Exception) as err:
            print("Failed to insert metadata of inversion process!")
            print(err)   
        
        # loop over the parameters stored in the LUT and generate the according synthetic spectra
        for ii in range(param_lut.lut_size):
            
            # run ProSAIL for each combination in the LUT
            n = param_lut.lut[0,ii]
            cab = param_lut.lut[1,ii]
            car = param_lut.lut[2,ii]
            cbrown = param_lut.lut[3,ii]
            cw = param_lut.lut[4,ii]
            cm = param_lut.lut[5,ii]
            lai = param_lut.lut[6,ii]
            lidfa = param_lut.lut[7,ii]
            lidfb = param_lut.lut[8,ii]
            rsoil = param_lut.lut[9,ii]
            psoil = param_lut.lut[10,ii]
            hspot = param_lut.lut[11,ii]
            tts = param_lut.lut[12,ii]
            tto = param_lut.lut[13,ii]
            psi = param_lut.lut[14,ii]
            typelidf = param_lut.lut[15,ii]
            
            # run prosail in forward mode -> resulting spectrum is from 400 to 2500 nm in 1nm steps
            # use Python ProSAIL bindings
            spectrum = prosail.run_prosail(n, cab, car,  cbrown, cw, cm, lai, lidfa, hspot,
                                           tts, tto, psi, ant=0.0, alpha=40., prospect_version="5", 
                                           typelidf=typelidf, lidfb=lidfb, rsoil0=soils[:,0],
                                           rsoil=1., psoil=1., factor="SDR")
            # resample to SRF of sensor
            # perform resampling from 1nm to S2-bands
            sensor_spectrum = resampler(spectrum)
            
            # convert to % reflectance
            sensor_spectrum *= 100.
        
            # store the results in DB
            insert_statement = "INSERT INTO {0} (id, n, cab, car, cbrown, cw, cm, " \
                                "lai, lidfa, lidfb, rsoil, psoil, hspot, tts, tto, psi, typelidf, " \
                                "b2, b3, b4, b5, b6, b7, b8a, b11, b12, acquisition_date, landuse) VALUES " \
                                "({1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, " \
                                "{12}, {13}, {14}, {15}, {16}, {17}, {18}, {19}, {20}, {21}, " \
                                "{22}, {23}, {24}, {25}, {26}, '{27}', {28});".format(
                                        inv_table,
                                        ii,
                                        np.round(n, 2),
                                        np.round(cab, 2),
                                        np.round(car, 2),
                                        np.round(cbrown, 2),
                                        np.round(cw, 2),
                                        np.round(cm, 2),
                                        np.round(lai, 2),
                                        np.round(lidfa, 2),
                                        np.round(lidfb, 2),
                                        np.round(rsoil, 2),
                                        np.round(psoil, 2),
                                        np.round(hspot, 2),
                                        np.round(tts, 4),
                                        np.round(tto, 4),
                                        np.round(psi, 4),
                                        np.round(typelidf, 2),
                                        np.round(sensor_spectrum[0], 4),
                                        np.round(sensor_spectrum[1], 4),
                                        np.round(sensor_spectrum[2], 4),
                                        np.round(sensor_spectrum[3], 4),
                                        np.round(sensor_spectrum[4], 4),
                                        np.round(sensor_spectrum[5], 4),
                                        np.round(sensor_spectrum[6], 4),
                                        np.round(sensor_spectrum[7], 4),
                                        np.round(sensor_spectrum[8], 4),
                                        acqui_date,
                                        luc
                                        )
            
            try:
                self.cursor.execute(insert_statement)
                self.conn.commit()
            except (Exception, psycopg2.DatabaseError):
                print("ERROR: INSERT of synthetic spectra failed!")
                continue
            
        # endfor -> lut_table is finished
        
    def do_obj_inversion(self, object_id, acqui_date, land_use, num_solutions, inv_params, res_table):
        """
        performs inversion per single object using mean of xx best
        solutions (RMSE criterion) and stores result results table
        params to be inverted/ returned should be passed as list of strings
        e.g: inv_params = ["LAI", "CAB"]
        also inverted spectra can be returned: therefore just append the band
        numbers to the list of strings of parameters:
        e.g. inv_params = ["LAI", "CAB", "B2", "B3", etc.]
        """
        
        query = """ SELECT 
                        lut.id,
                        rmse(obj.b2, obj.b3, obj.b4, obj.b5, obj.b6, obj.b7,
                             obj.b8a, obj.b11, obj.b12,lut.b2, lut.b3, lut.b4, 
                             lut.b5, lut.b6, lut.b7, lut.b8a, lut.b11, lut.b12) 
                        AS rmse
                    FROM
                        s2_obj_spec as obj,
                        s2_lut as lut
                    WHERE
                        obj.object_id = {0}
                    AND
                       obj.acquisition_date = '{1}'
                    AND
                       obj.landuse = {2}
                    AND
                        obj.landuse = lut.landuse
                    AND
                        obj.acquisition_date = lut.acquisition_date
                    ORDER BY rmse ASC
                    LIMIT {3};""".format(
                    object_id,
                    acqui_date,
                    land_use,
                    num_solutions)
        
        try:
            
            self.cursor.execute(query)
            inv_res = self.cursor.fetchall()
            
            lut_ids = [item[0] for item in inv_res]
            rmse_vals = [item[1] for item in inv_res]
            
            # convert lut_ids to str
            lut_ids = str(lut_ids)
            lut_ids = lut_ids.replace("[", "(")
            lut_ids = lut_ids.replace("]", ")")
            
            # convert the params to be inverted in the correct format
            # for SQL-query
            sql_snippets = []
            for param in inv_params:
                sql_snippet = "AVG(" + param + ")"
                sql_snippets.append(sql_snippet)
            # endfor
            sql_snippets = str(sql_snippets)
            sql_snippets = sql_snippets[1:len(sql_snippets)-1]
            sql_snippets = sql_snippets.replace("'", "")
            
            # select the biophysical parameters from the xx best solutions in the
            # lut table using the lut ids as keys
            query = "SELECT {0} FROM s2_lut WHERE id in {1};".format(
                    sql_snippets,
                    lut_ids)
            
            try:
                self.cursor.execute(query)
                mean_params = self.cursor.fetchall()
                
                # convert result to dictionary for storing results in DB
                result_dict = dict()
                
                index = 0
                for param in inv_params:
                    result_dict[param] = mean_params[0][index]
                    index += 1
                
                # also store the errors
                error_dict = dict()
                for ii in range(num_solutions):
                    error_dict[str(ii+1)] = rmse_vals[ii]
                
                # convert to json
                result_json = json.dumps(result_dict)
                error_json = json.dumps(error_dict)
                
                # insert statement
                insert = "INSERT INTO {0} VALUES ({1}, '{2}', '{3}', '{4}');".format(
                        res_table,
                        object_id,
                        acqui_date,
                        result_json,
                        error_json
                        )
                
                try:
                    self.cursor.execute(insert)
                    self.conn.commit()
                except Exception:
                    print("ERROR: Insert of results for object {0} failed!".format(
                            object_id))
                    return -1
            
            except Exception:
                print("Error: No inversion result could be obtained for object {0}".format(
                        object_id))
                return -1
            
        except Exception as err:
            
            print("ERROR: Inverting object with id {0} failed".format(object_id))
            print(err)
            return -1
        
        # return zero if everything was OK
        return 0
    # end function
    
    def do_inversion(self, acqui_date, land_use, num_solutions, res_table, return_specs=True):
        """
        performs inversion on all objects for a given date
        """
        # get list of objects available for a given land use class at a given day
        query = "SELECT DISTINCT object_id FROM s2_obj_spec " \
                " WHERE acquisition_date = '{0}'" \
                " AND landuse = {1};".format(
                        acqui_date,
                        land_use)
        try:
            self.cursor.execute(query)
            object_ids = self.cursor.fetchall()
            object_ids = [item[0] for item in object_ids]
            
        except Exception as err:
            print("ERROR: Could not query objects for acquistion date {0} and LUC {1}".format(
                    acqui_date,
                    land_use))
            print(err)
            sys.exit(-1)
        
        # get the list of params to be inverted
        query = "SELECT params_to_be_inverted FROM inversion_mapping" \
                " WHERE acquisition_date = '{0}' AND landuse = {1};".format(
                        acqui_date,
                        land_use
                        )
        
        try:
            self.cursor.execute(query)
            params = self.cursor.fetchall()
            params_dict = params[0][0]
            # convert to list
            params_list = []
            for key, val in params_dict.items():
                params_list.append(val)
            
            # if inverted spectra should be returned add them to params_list
            if (return_specs):
                band_names = ["B2", "B3", "B4", "B5", "B6", "B7", "B8A", "B11", "B12"]
                for band_name in band_names:
                    params_list.append(band_name)
                # endfor
            # endif
            
        except Exception as err:
            
            print("ERROR: Retrieving inversion metadata for acquisition date {0} and LUC {1} failed!".format(
                    acqui_date,
                    land_use))
            print(err)
            sys.exit(-1)
        
        # iterate over all objects to perform the inversion per object
        for ii in range(len(object_ids)):
            
            object_id = object_ids[ii]
            resrun = self.do_obj_inversion(object_id, acqui_date, land_use, 
                                           num_solutions, params_list, res_table)
            
            # in case an error happened
            if resrun != 0:
                self.conn.rollback()
                continue
        
        
           