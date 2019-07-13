#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 13 09:44:14 2019

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
import os
import sys
from configparser import ConfigParser
import psycopg2
import OBIA4RTM

def connect_db():
    """
    connect to PostgreSQL database by using the specifications
    in 'postgres.ini' File in the root of the OBIA4RTM package
    
    Returns
    -------
    conn : psycopg2 Database connection
        connection object to PostgreSQL database
    cursor psycopg2 Database cursor
        cursor for querying and inserting data from and to PostgreSQL DB
    """
    try:
        # read the connection parameters from config-file (see template postgres.ini)
        parser = ConfigParser()
        directory = os.path.dirname(OBIA4RTM.__file__)
        postgres_init = directory + os.sep + 'postgres.ini'
        if not os.path.isfile(postgres_init):
            print('postgres.ini konnte nicht gefunden werden!')
            sys.exit(-1)
        parser.read(postgres_init)
        # and store them in a string
        conn_str = "host='{}' dbname='{}' user='{}' password='{}'". format(
                parser.get('POSTGRESQL', 'host'),
                parser.get('POSTGRESQL', 'dbname'),
                parser.get('POSTGRESQL', 'username'),
                parser.get('POSTGRESQL', 'password')
                )
        # open connection
        conn = psycopg2.connect(conn_str)
        cursor = conn.cursor()
    except (psycopg2.DatabaseError) as err:
        print ("ERROR: Unable to connect to the database")
        print (err)
        sys.exit(-1)
    # return conn und cursor objects
    return conn, cursor
