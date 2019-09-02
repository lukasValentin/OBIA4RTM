#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 14:11:59 2019

This module is part of OBIA4RTM.

Copyright (c) 2019 Lukas Graf

@author: Lukas Graf, graflukas@web.de
"""
import os
import logging
import logging.handlers
import OBIA4RTM


def determine_logdir():
    """
    searches the logging directory used for OBIA4RTM

    Returns
    -------
    log_dir : String
        Path of logging directory
    """
    obia4rtm_dir = os.path.dirname(OBIA4RTM.__file__)
    # open the OBIA4RTM_HOME file that tells where to look for the logging
    # diretory
    fname = obia4rtm_dir + os.sep + 'OBIA4RTM_HOME'
    with open(fname, 'r') as data:
        logging_dir = data.readline()
    try:
        assert logging_dir is not None and logging_dir != ''
    except AssertionError:
        raise AssertionError
    logging_dir = logging_dir + os.sep + 'log'
    # return the logging dir
    return logging_dir


def get_logger(logname=None):
    """
    setups up a new logging object using Rotating File Handlers

    Parameters
    ----------
    OBIA4RTM_log_dir : String
        directory, the log-file should be written to
    logname : String
        name of the logger (opt.); per default OBIA4RTM_Logger will be used

    Returns
    ------
    logger : logging Logger
        Logger with stream handler for tracing OBIA4RTM's activities and errors
    """
    # determine the logging directory of OBIA4RTM (somewhere in the user profile)
    OBIA4RTM_log_dir = determine_logdir()
    # create a new handler for the logging output
    fname = OBIA4RTM_log_dir + os.sep + 'OBIA4RTM.log'
    # use rotating file handler; a new file will be opened when the size
    # of the log-file exceeds 10 000 bytes
    logHandler = logging.handlers.RotatingFileHandler(fname, maxBytes=10000)
    # set the format
    logFormat = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logHandler.setFormatter(logFormat)
    # get a new logger
    # set up a log file name if None was provided
    if logname is None:
        logname = 'OBIA4RTM_Logger'
    logger = logging.getLogger(logname)
     # set logging level to DEBUG
    logger.setLevel(level=logging.DEBUG)
    # add the handler to the logger
    logger.addHandler(logHandler)
    # return the logger to the calling module
    return logger


def close_logger(logger):
    """
    close a logger after program shut-down and releases the handlers

    Parameters
    ----------
    logger : logging Object
        logger of OBIA4RTM 'OBIA4RTM_logger'
    """
    # get the handlers and close them one by one
    handlers = logger.handlers[:]
    for handler in handlers:
        handler.close()
        logger.removeHandler(handler)
