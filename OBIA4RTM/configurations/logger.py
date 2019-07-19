#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 14:11:59 2019

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
import logging


def get_logger(OBIA4RTM_log_dir, logname=None):
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
