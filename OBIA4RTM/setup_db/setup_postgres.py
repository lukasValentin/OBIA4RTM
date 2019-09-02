#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 15:08:29 2019

This module is part of OBIA4RTM.

Copyright (c) 2019 Lukas Graf

@author: Lukas Graf, graflukas@web.de
"""
import os
import sys
from psycopg2 import connect, DatabaseError, ProgrammingError
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import OBIA4RTM
from OBIA4RTM.configurations.connect_db import connect_db, close_db_connection
from OBIA4RTM.configurations.connect_db import get_db_connection_details


class setupDataBase:
    """
    class for setting up a PostgresSQL database as backend for OBIA4RTM
    """
    def __init__(self):
        """
        class constructor
        """
        # set the path to SQL-scripts
        self.sql_home = os.path.dirname(OBIA4RTM.__file__) + os.sep + 'SQL'
        self.__postgres_params = get_db_connection_details()
        # setup connection and cursor to database
        self.__con, self.__cursor = None, None


    def connect_to_postgres(self):
        """
        connects to default Postgres database running on specified host in
        postgres.ini file to create the OBIA4RTM Postgres database

        Returns
        -------
        con : psycopg2 Database Connection
            Connection to DEFAULT Postges database (not OBIA4RTM database)
        cursor : psycopg2 Database Cursor
            Cursor for this default database
        """
        # host and password for DEFAULT postgres database
        host = self.__postgres_params.get('POSTGRESQL', 'host')
        pw = self.__postgres_params.get('POSTGRESQL', 'password')
        # default database name is postgres
        db_name = 'postgres'
        # user is postgres
        db_user = 'postgres'
        # connect to default database
        try:
            con = connect(dbname=db_name,
                          user=db_user,
                          host=host,
                          password=pw)
            cursor = con.cursor()
        except DatabaseError as err:
            print('Connection to default Postgres Database failed!\nReason: {}'.format(
                    err))
        return con, cursor


    def create_OBIA4RTM_DB(self):
        """
        create the OBIA4RTM database using the specification of the postgres.uni
        file

        Returns
        -------
        status : Integer
            zero, if everything was OK
        """
        # open connection to default postgres database
        con, cursor = self.connect_to_postgres()
        # set autocommit to allow for the creation of databases
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        # use the name of the OBIA4RTM database parsed from the postgres.ini file
        obia4rtm_db_name = self.__postgres_params.get('POSTGRESQL', 'dbname')
        # parse the SQL script for setting up the database
        sql_file = self.sql_home + os.sep + 'Tables' + os.sep + 'setup_obia4rtm_db.sql'
        # try to read in the SQL-statement of the script and replace the
        # the database-name accordingly
        try:
            fopen = open(sql_file, "r")
            lines = fopen.readlines()
            fopen.close()
        except IOError as err:
            print('Failed to read the SQL-script\nReason: {}'.format(err))
        # extract the SQL statement
        # '--' indicates comments
        comment = '--'
        sql_statement = [''.join(f.replace("\n","")) for f in lines if comment not in f]
        sql_statement = ''.join(map(str, sql_statement))
        # replace the default database-name
        default_db_name = "OBIA4RTM"
        sql_statement = sql_statement.replace(default_db_name, obia4rtm_db_name)
        # run the statement to create the database
        try:
            cursor.execute(sql_statement)
            con.commit()
        except (DatabaseError, ProgrammingError) as err:
            print("Setup of DB '{0}' failed!\nReason: {1}".format(
                    obia4rtm_db_name, err))
        # close the connection as it won't be used anymore
        close_db_connection(con, cursor)
        return 0


    def enable_extensions(self):
        """ 
        enables PostGIS and HSTORE extension required for OBIA4RTM
        """
        # connect to the created database
        self.__con, self.__cursor = connect_db()
        # enable the PostGIS extension
        sql = "CREATE EXTENSION PostGIS;"
        try:
            self.__cursor.execute(sql)
            self.__con.commit()
        except (ProgrammingError, DatabaseError):
            print("PostGIS setup failed!")
            sys.exit(-1)
        # enable the HSTORE extension
        sql = "CREATE EXTENSION HSTORE;"
        try:
            self.__cursor.execute(sql)
            self.__con.commit()
        except (ProgrammingError, DatabaseError):
            print("HSTORE setup failed!")
            sys.exit(-1)


    def setup_public_tables(self):
        """
        setups all those tables, that are required in the public schema
        of the OBIa4RTM backend database
        """
        # the following tables are in the public schema and are created
        # by the according sql-scripts
        # the s2_bands table is a bit special and follows
        public_tables = ['s2_landuse.sql', 'scene_metadata.sql']
        # '--' indicates comments
        comment = '--'
        # loop over scripts
        for sql_file in public_tables:
            sql_file = self.sql_home + os.sep + 'Tables' + os.sep + sql_file
            try:
                fopen = open(sql_file, "r")
                lines = fopen.readlines()
                fopen.close()
            except IOError as err:
                print('Failed to read the SQL-script{0}\nReason: {1}'.format(
                        sql_file, err))
            # extract the SQL statement
            sql_statement = [''.join(f.replace("\n","")) for f in lines if comment not in f]
            sql_statement = ''.join(map(str, sql_statement))
            try:
                self.__cursor.execute(sql_statement)
                self.__con.commit()
            except (DatabaseError, ProgrammingError) as err:
                print("Execution of script '{0}' failed!\nReason: {1}".format(
                        sql_file, err))
        # end loop
        # now read in the Sentinel-2 bands sql script and execute it
        s2_band_table = self.sql_home + os.sep + 'Tables' + os.sep + 's2_bands.sql'
        try:
            fopen = open(s2_band_table, "r")
            lines = fopen.readlines()
            fopen.close()
        except IOError as err:
            print('Failed to read the SQL-script{0}\nReason: {1}'.format(
                        sql_file, err))
        # extract the sql-statement
        sql_statement = [''.join(f.replace("\n","")) for f in lines if comment not in f]
        # the first 12 lines form the first statement for creating the table
        sql_statement_1 = sql_statement[0:12]
        sql_statement_1 = ''.join(map(str, sql_statement_1))
        try:
            self.__cursor.execute(sql_statement_1)
            self.__con.commit()
        except (DatabaseError, ProgrammingError) as err:
            print("Execution of script '{0}' failed!\nReason: {1}".format(
                    sql_file, err))
        # the next lines must be executed line by line as they populate the
        # table created above with the necessary data
        sql_statement = sql_statement[14::]
        # iterate over the single lines(=SQL statements) to populate the table
        for sql in sql_statement:
            # leave out empty lines
            if sql == '':
                continue
            try:
                self.__cursor.execute(sql)
                self.__con.commit()
            except (DatabaseError, ProgrammingError) as err:
                print(err)
                self.__con.rollback()
                continue
        # end iterate over statements


    def setup_public_functions(self):
        """
        setups the RMSE function used in OBIA4RTM for doing the inversion
        """
        # name and location of the sql script with RMSe function
        sql_file = self.sql_home + os.sep + 'Queries_Functions' + os.sep + 'rmse_function.sql'
        try:
            fopen = open(sql_file, "r")
            lines = fopen.readlines()
            fopen.close()
        except IOError as err:
            print('Failed to read the SQL-script{0}\nReason: {1}'.format(
                    sql_file, err))
        # '--' indicates comments
        comment = '--'
        sql_statement = [''.join(f.replace("\n","")) for f in lines if comment not in f]
        sql_statement = ''.join(map(str, sql_statement))
        try:
            self.__cursor.execute(sql_statement)
            self.__con.commit()
        except (DatabaseError, ProgrammingError) as err:
            print("Execution of script '{0}' failed!\nReason: {1}".format(
                    sql_file, err))


    def setup_backend(self):
        """
        runs the whole setup-procedure for creating the OBIA4RTM backend
        """
        # first the OBIA4RTM database needs to be created
        print('Settting up OBIA4RTM PostgreSQL backend')
        status = self.create_OBIA4RTM_DB()
        if status != 0:
            print('OBIA4RTM backend setup failed!')
            sys.exit(-1)
        # enable the PostGIS and Hstore extensions
        self.enable_extensions()
        # then create the public tables and functions
        self.setup_public_tables()
        self.setup_public_functions()
        # at the end, close the database connection
        close_db_connection(self.__con, self.__cursor)
        print('Successfully set up OBIA4RTM backend!')
