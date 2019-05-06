#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  6 13:09:42 2019

@author: lukas

to do: -> go to Sen2Core result directory
"""

from OBIA4RTM.mdata_proc.parse_s2xml import parse_s2xml


def run_xml_parser(path_to_xml):
    """
    calls parse_s2xml for reading in the metadata into a dictionary
    """
    metadata = parse_s2xml(path_to_xml)
    
    if metadata is None:
        print("Reading of Metadata from xml failed!")
    # endif
    