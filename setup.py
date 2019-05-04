#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import setuptools
from os import path

home = path.abspath(path.dirname(__file__))
with open(path.join(home, 'README.md'), encoding='utf-8') as readme:
    long_description = readme.read()


setuptools.setup(name='OBIA4RTM',
      version = '1.0',
      description = 'Object-Based Image Analysis Tools for Radiative Transfer Modelling',
      long_description = long_description,
      long_description_content_type = 'text/markdown',
      author='Lukas Graf',
      author_email =' lukas.graf@stud.sbg.ac.at',
      url = 'https://github.com/lukasValentin/OBIA4RTM',
      packages=setuptools.find_packages(
            "psycopg2",
            "numpy",
            "prosail"
            ),
      classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
     )