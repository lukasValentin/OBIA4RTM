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
      author_email ='graflukas@web.de',
      url = 'https://github.com/lukasValentin/OBIA4RTM',
      include_package_data=True,
      package_data={'OBIA4RTM': ['postgres.ini', 'landcover.cfg', 'prosail.txt', 'soil_relfectance.txt', 'obia4rtm_backend.cfg', 'OBIA4RTM_HOME', './SQL/Tables/*.sql', './SQL/Queries_Functions/*.sql']},
      packages=setuptools.find_packages(),
      classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Non-commercial usage for education and research",
        "Operating System :: OS Independent",
    ],
     )
