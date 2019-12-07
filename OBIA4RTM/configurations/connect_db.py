#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 13 09:44:14 2019

This module is part of OBIA4RTM.

Copyright (c) 2019 Lukas Graf

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
    in 'postgres.ini' File in the root of the OBIA4RTM home directory
    stored in the user-profile
    
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
            print('postgres.ini could not be found!')
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


def get_db_connection_details():
    """
    reads and returns the postgres.ini connection details
    
    Returns:
    -------
    parser : ConfigParser Object
        parsed database configurations from postgres.ini file
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
    except (IOError) as err:
        print ("Reading from postgres.ini failed")
        print (err)
        sys.exit(-1)
    # return conn und cursor objects
    return parser


def close_db_connection(con, cursor):
    """
    closes an opened database connection

    Parameters
    ----------
    con : psycopg2 Database Connection
        connection to be closed
    cursor : psycopg2 Database Cursor
        cursor to be closed
    """
    # check if con is still a valid connection
    if con is not None:
        # close first the cursor and then con
        cursor.close()
        con.close()
