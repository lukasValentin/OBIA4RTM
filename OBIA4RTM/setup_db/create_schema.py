#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 10:15:38 2019

This module is part of OBIA4RTM.

Copyright (c) 2019 Lukas Graf

@author: Lukas Graf, graflukas@web.de
"""
import os
import sys
from psycopg2 import DatabaseError,ProgrammingError
from configparser import ConfigParser, MissingSectionHeaderError
import OBIA4RTM
from OBIA4RTM.configurations.logger import get_logger, close_logger
from OBIA4RTM.configurations.connect_db import connect_db, close_db_connection


sys_exit_message = 'An error occured during setup of new Postgres schema. Check log!'


def create_schema():
    """
    this function is used to generate a new schema in the OBIA4RTM database.
    In case the schema already exists, nothing will happen.
    The schema to be created is taken from the obia4rtm_backend.cfg file

    Parameters
    ----------
    None

    Returns
    -------
    status : integer
        zero if everything was OK
    """
    status = 0
    # connect to OBIA4RTM database
    con, cursor = connect_db()
    # open a logger
    logger = get_logger()
    logger.info('Trying to setup a new schema for the OBIA4RTM database')
    # read in the obia4rtm_backend information to get the name of the schema
    # therefore the obia4rtm_backend.cfg file must be read
    install_dir = os.path.dirname(OBIA4RTM.__file__)
    home_pointer = install_dir + os.sep + 'OBIA4RTM_HOME'
    if not os.path.isfile(home_pointer):
        logger.error('Cannot determine OBIA4RTM Home directory!')
        close_logger(logger)
        sys.exit(-1)
    with open(home_pointer, "r") as data:
        obia4rtm_home = data.read()
    backend_cfg = obia4rtm_home + os.sep + 'obia4rtm_backend.cfg'
    if not os.path.isfile(backend_cfg):
        logger.error('Cannot read obia4rtm_backend.cfg from {}!'.format(
                obia4rtm_home))
        close_logger(logger)
        sys.exit(sys_exit_message)
    # now, the cfg information can be read in using the configParser class
    parser = ConfigParser()
    try:
        parser.read(backend_cfg)
    except MissingSectionHeaderError:
        logger.error('The obia4rtm_backend.cfg does not fulfil the formal requirements!',
                     exc_info=True)
        close_logger(logger)
        sys.exit(-1)
    # no get the name of the schema
    schema = parser.get('schema-setting', 'schema_obia4rtm')
    try:
        assert schema is not None and schema != ''
    except AssertionError:
        logger.error('The version of your obia4rtm_backend.cfg file seems to be corrupt!',
                     exc_info=True)
        close_logger(logger)
        sys.exit(sys_exit_message)
    # if the schema name is OK, the schema can be created
    # if the schema already exists in the current database, nothing will happen
    sql = 'CREATE SCHEMA IF NOT EXISTS {};'.format(schema)
    cursor.execute(sql)
    con.commit()
    # enable PostGIS and HSTORE extension
    # enable the PostGIS extension
    # in case it fails it is most likely because the extension was almost
    # enabled as it should
    sql = "CREATE EXTENSION PostGIS;"
    try:
        cursor.execute(sql)
        con.commit()
    except (ProgrammingError, DatabaseError):
        logger.info("PostGIS already enabled!")
        con.rollback()
        pass
    # enable the HSTORE extension
    sql = "CREATE EXTENSION HSTORE;"
    try:
        cursor.execute(sql)
        con.commit()
    except (ProgrammingError, DatabaseError):
        logger.error("HSTORE already enabled!")
        con.rollback()
        pass

    logger.info("Successfully created schema '{}' in current OBIA4RTM database!".format(
            schema))
    # after that the schema-specific tables are created that are required
    # in OBIA4RTM
    sql_home = install_dir + os.sep + 'SQL' + os.sep + 'Tables'
    # the tables 's2_inversion_results, s2_lookuptable, s2_objects and s2_inversion_mapping
    # must be created within the schema
    # check if the tables already exist before trying to create them
    sql_scripts = ['s2_lookuptable.sql','s2_inversion_results.sql', 's2_objects.sql', 'inversion_mapping.sql']
    # go through the config file to get the table-names
    table_names = []
    table_names.append(parser.get('schema-setting', 'table_lookuptabe'))
    table_names.append(parser.get('schema-setting', 'table_inv_results'))
    table_names.append(parser.get('schema-setting', 'table_object_spectra'))
    table_names.append(parser.get('schema-setting', 'table_inv_mapping'))
    # the parser can be cleared now as all information is read
    parser.clear()
    # iterate through the 4 scripts to create the tables given they not exist
    for index in range(len(sql_scripts)):
        sql_script = sql_home + os.sep + sql_scripts[index]
        table_name = table_names[index]
        # check if the table already exists
        exists = check_if_exists(schema, table_name, cursor)
        # if already exists table log a warning and continue with the next table
        if exists:
            logger.warning("Table '{0}' already exists in schema '{1}' - skipping".format(
                    table_name,
                    schema))
            continue
        # else create the table
        # get the corresponding sql-statment and try to execute it
        sql_statement = create_sql_statement(sql_script,
                                             schema,
                                             table_name,
                                             logger)
        try:
            cursor.execute(sql_statement)
            con.commit()
        except (DatabaseError, ProgrammingError):
            logger.error("Creating table '{0}' in schema '{1}' failed!".format(
                    table_name, schema), exc_info=True)
            close_logger(logger)
            sys.exit(sys_exit_message)
        # log success
        logger.info("Successfully created table '{0}' in schema '{1}'".format(
                table_name, schema))
    # create the RMSE function required for inverting the spectra
    fun_home = install_dir + os.sep + 'SQL' + os.sep + 'Queries_Functions'
    rmse_fun = fun_home + os.sep + 'rmse_function.sql'
    sql_statement = create_function_statement(rmse_fun, logger)
    try:
        cursor.execute(sql_statement)
        con.commit()
    except (DatabaseError, ProgrammingError):
        logger.error("Creating function '{0}' failed!".format(
                rmse_fun), exc_info=True)
        close_logger(logger)
        sys.exit(sys_exit_message)
    # after iterating, the db connection and the logger can be close
    close_db_connection(con, cursor)
    close_logger(logger)
    return status


def create_sql_statement(sql_file, schema, table_name, logger):
    """
    auxiiliary function to create the sql_statement required to create
    the specific tables in the DB schema

    Parameters
    ----------
    sql_file : String
        file-path to the sql-template containing the sql-statement for creating the table
    schema : String
        name of the schema the table should be created in
    table_name : String
        name of the table to be created
    logger : logging.Logger
        for logging errors

    Returns
    -------
    sql_statement : String
        processed and ready-to-execute sql statement
    """
    try:
        fopen = open(sql_file, "r")
        lines = fopen.readlines()
        fopen.close()
    except IOError:
        logger.error('Failed to read the SQL-script\nReason:', exc_info=True)
        close_logger(logger)
        sys.exit(sys_exit_message)
    # extract the SQL statement
    # '--' indicates comments
    comment = '--'
    sql_statement = [''.join(f.replace("\n","")) for f in lines if comment not in f]
    sql_statement = ''.join(map(str, sql_statement))
    # now, replace "schema_name" and "table_name" with their actual values
    sql_statement = sql_statement.replace('schema_name', schema)
    sql_statement = sql_statement.replace('table_name', table_name)
    return sql_statement


def create_function_statement(sql_function, logger):
    """
    create a SQL statement for creating/ replacing a SQL function

    Parameters
    ----------
    sql_function : String
        file-path to the sql-function
    logger : logging.Logger
        for logging errors

    Returns
    -------
    sql_statement : String
        processed and ready-to-execute sql statement
    """
    try:
        fopen = open(sql_function, "r")
        lines = fopen.readlines()
        fopen.close()
    except IOError:
        logger.error('Failed to read the SQL-script\nReason:', exc_info=True)
        close_logger(logger)
        sys.exit(sys_exit_message)
    # extract the SQL statement
    # '--' indicates comments
    comment = '--'
    sql_statement = [''.join(f.replace("\n","")) for f in lines if comment not in f]
    sql_statement = ''.join(map(str, sql_statement))
    return sql_statement


def check_if_exists(schema, table_name, cursor):
    """
    auxiiliary function to check whether a given table exists in a given schema

    Parameters
    ----------
    schema : String
        name of the schema the table should be created in
    table_name : String
        name of the table to be created
    cursor : psycopg2 Database Cursor
        for querying the database

    Returns
    -------
    exists : Boolean
        True, if table already exists, False else
    """
    sql = """SELECT EXISTS (
        SELECT 1
        FROM   information_schema.tables 
        WHERE  table_schema = '{0}'
        AND    table_name = '{1}'
        );""".format(
        schema.lower(),
        table_name.lower())
    cursor.execute(sql)
    exists = cursor.fetchone()[0]
    return exists
