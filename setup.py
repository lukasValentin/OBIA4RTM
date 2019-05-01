#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import setuptools

setuptools.setup(name='OBIA4RTM',
      version='1.0',
      description='Object-Based Image Analysis Tools for Radiative Transfer Modelling',
      author='Lukas Graf',
      author_email='lukas.graf@stud.sbg.ac.at',
      url='',
      packages=setuptools.find_packages(
            "psycopg2",
            "numpy",
            "prosail"
            ),
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
     )