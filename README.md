[logo]: https://github.com/lukasValentin/OBIA4RTM/blob/master/obia4rtm_logo.JPG "OBIA4RTM logo"
**OBIA4RTM**
------------
[![DOI](https://zenodo.org/badge/184379375.svg)](https://zenodo.org/badge/latestdoi/184379375) [![Python 3.6](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/) [![Coverage Status](https://coveralls.io/repos/github/lukasValentin/OBIA4RTM/badge.svg?branch=master)](https://coveralls.io/github/lukasValentin/OBIA4RTM?branch=master) [![Build Status](https://travis-ci.com/lukasValentin/OBIA4RTM.svg?branch=master)](https://travis-ci.com/lukasValentin/OBIA4RTM) [![Documentation Status](https://readthedocs.org/projects/obia4rtm/badge/?version=latest)](https://obia4rtm.readthedocs.io/en/latest/genindex.html) [![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

An open-source tool for object-based image analysis for radiative transfer modeling
using ProSAIL (Prospect5 + 4SAIL) free for non-commercial applications (research and education) under **Creative Commons Attribution-NonCommercial 4.0 International Public License**.

**IMPORTANT**	OBIA4RTM is currently just a first prototype and will continously updated. Therefore, **contributions** (see below) are welcomed!

If you'd like to see how **`OBIA4RTM works in practice`** have a look at this [new repository](https://github.com/lukasValentin/OBIA4RTM-Agricultural-Example) that provides some insights into and results from an agricultural use case.

About OBIA4RTM
--------------

OBIA4RTM aims for **`plant parameter retrieval`** - relevant in *smart farming* applications - by using **`radiative transfer models (RTM)`** and **`object-based image analysis (OBIA)`** that
direclty addresses actual user needs and policy demands in a highly efficient, flexible and scalable way. It uses optical satellite data (concurrently **Sentinel-2**) as input.

The RTM approach makes the tool transferable and nearly globally applicable to a broad range of different crop types, while OBIA accounts for producing results on a per-object rather than per pixel-base. Image objects have the distinct advantage of being directly related to real-world entities such as single field parcels. Furthermore, results on a per-object base can be easily managed and shared via geospatial databases and web-interfaces and refer also to the requirements of the Big-Data era.

The basis idea of OBIA4RTM is to combine to widely used Remote Sensing analysis techniques:

The biophysical parameter retrieval from optical imagery by means of radiative transfer modelling (RTM) and the object-based image analysis (OBIA) concept. While RTM accounts for retrieving the most relevant plant parameters relevant in farming context (Leaf Area Index, Leaf Chlorophyll Content, etc.), the OBIA approach allows for semantic enrichment of spectral data by means of **incorporating expert knowledge and advanced spatial analysis techniques**.

OBIA4RTM relies therefore on two main pillars: It describes plant spectra by means of physical equations that are universally applicable by using RTM and it introduces the concept of spatial autocorrelation to reduce redundancies and provide more meaningful image objects by means of OBIA. It is thereby capable to provide vegetation parameter retrieval techniques that are not bound by temporal or geographic restrictions. Furthermore, **OBIA4RTM directly addresses objects and, thus, human needs** as humans tend not to think in artificial spatial units (i.e. pixels)
but in terms of tangible entities such as single field patches or individual trees in an orchard.

Contributing
------------

Contribution to OBIA4RTM is more than welcomed! My time resources are limited and in case you are interested in the topic and you have ideas about

- improving the code (since it is not always implemented very efficiently ;) )
- adding additional features
- testing the functionalities and reporting bugs
- improving the usability
- etc.

you are invited to join!


Workflow
--------

The overall workflow implemented in OBIA4RTM is shown below.

## Inputs

OBIA4RTM currently expects **Sentinel-2** imagery in **Level-2A** (i.e. corrected for atmospheric effects). Per default it is assumed that Sen2Core was used for generating the Level-2A data (see: http://step.esa.int/main/third-party-plugins-2/sen2cor/) or data was almost downloaded in this processing level from Copernicus or any other (national) data hub.
**OBIA4RTM offers a convenient wrapper around the Sen2Core command line tool** that takes about all the preprocessing and formatting steps. This wrapper works independently of OBIA4RTM in the sense that it does not interact with the OBIA4RTM database. In can be therefore also used for other Sentinel-2 preprocessing workflows.

Optionally, preprocessing can be also done using **Google Earth Engine** (optionally) which makes OBIA4RTM a **zero-download** program as not imagery is downloaded expect the object spectra that are directly written to the OBIA4RTM database.

![OBIA4RTM Workflow](https://github.com/lukasValentin/OBIA4RTM/blob/master/OBIA4RTM_Workflow.gif "OBIA4RTM Workflow Overview")


It should be noted, that:

- OBIA4RTM expects stacked Sentinel-2 (A and B) image data as GeoTiff-File. Only the following Sentinel-2 bands (wavelengths and bandwidths shown for Sentinel-2A only) are used: 

Band Number  |	Central wavelength (nm)	|  Bandwidth (nm)  |  Spatial resolution (m)
-----------  |  ----------------------- |  --------------  |  ----------------------
2    |	492.4  |	66	| 10
3    |	559.8  |	36	| 10
4    |	664.6  |	31	| 10
5    |	704.1  |	15	| 20
6    |	740.5  |	15	| 20
7    |	782.8  |	20	| 20
8a   |	864.7  |	21	| 20
11   |	1613.7 |	91	| 20
12   |	2202.4 |	175	| 20

- Scene metadata is read directly from either the Sen2Core provided metadata file (or in case you have already acquired Level-2A data the equivalent xml file) or by using the Google-Earth-Engine derived scene metadata. Without this metadata information, OBIA4RTM cannot be executed!

- the use of Copernicus land monitoring data is just a *suggestion*. Users can use also different land cover/ use classification or can even provide no classification at all (then all objects will be treated equally, otherwise, vegetation parameters have to be set per land use class).

- OBIA4RTM does not provide any image segementation facilities as there are lots of freely available image segmentation algorithms available (e.g. within the **Orfeo-Toolbox**).

- concurrently, OBIA4RTM uses the Root Mean Squared Error (RMSE) as cost function within the inversion strategy. Users can specify their own cost-functions. It is planned to add more cost functions in the future.

- all image objects are stored in a PostgreSQL database with PostGIS extension. Make sure to have PostgreSQL **and** PostGIS installed on your machine or where-ever you want to run OBIA4RTM.

Installation
------------

The installation of OBIA4RTM is multi-step procedure. It is suggested to start installing all dependencies first and then building the OBIA4RTM package using the setup.py file.

### PostgreSQL and PostGIS installation

The OBIA4RTM backend requires **PostgreSQL** for storing the information in a hybrid database (i.e. mainly relational with some object-oriented features). OBIA4RTM was mainly developed under PostgreSQL 10.9 but it is assumed that higher versions (>11.0) should work as well. For installing PostgreSQL you can refer this [tutorial for Windows](http://www.postgresqltutorial.com/install-postgresql/) or use this [instructions under Ubuntu](https://www.postgresql.org/download/linux/ubuntu/).

After having installed PostgreSQL, **PostGIS** is required to make PostgreSQL become a spatial database. For installation instructions, please see [here](https://postgis.net/install/).

### Python Packages

OBIA4RTM depends on a set of non-standard **Python-3** packages that are required to make the software running. **NOTE** that Python 2.x is not supported by OBIA4RTM as Python2 will reach its end of lifecycle in the near future!

Only the Google Earth Engine Python-API as well as Py6S are optional packages that users might skip. It is recommended to use [Anaconda](https://anaconda.org/anaconda) for the Python package management especially if you are planning to deploy OBIA4RTM under Windows. Especially the Setup of GDAL and the required RTM modules worked out smoothly under Windows when using Anaconda and installling directly from the Anaconda cloud.

You can install the following packages from the Anaconda command prompt:

```console
$ conda install -c conda-forge spectral
$ conda install -c anaconda scipy
$ conda install -c anaconda psycopg2
$ conda install -c conda-forge gdal
$ conda install -c jgomezdans prosail
$ conda install -c anaconda numpy
```

In case your planning to use Google Earth Engine (GEE), make sure to also install

```console
$ conda install -c conda-forge earthengine-api
$ conda install -c conda-forge Py6S
```

See also the instructions [how to use GEE Python API](https://developers.google.com/earth-engine/python_install).

### OBIA4RTM setup

First, clone or download OBIA4RTM from Github (as long as no PyPi/ Anaconda package is available):

```console
$ git clone https://github.com/lukasValentin/OBIA4RTM.git
```

Then go into the OBIA4RTM directory (cd ./OBIA4RTM) and run either 

```console
$ python3 -m pip install .
```

or 

```console
$ python3 setup.py install
```

to use either pip or the more advanced egg-installation.

After that, OBIA4RTM **is installed but not ready to use**. Therefore, open a Python3 session and type in

```python
from OBIA4RTM import install
install.install()
```
This installation script will take care about the database setup (including the creation of tables and functions) and enable the required extensions. Moreover, it will copy some configuration files into a **OBIA4RTM home directory** in the user profile. After having successfully run the installation script, OBIA4RTM is ready to use.

Usage Instructions
------------------

### Configuring OBIA4RTM

OBIA4RTM has a set of configuration files which are important for running the software:

- a configuration file that holds the **connection parameters of the PostgreSQL backend database** (*'postgres.ini'*). In case you want to use a different database instead of the default one, you have to set the connection parameters accordingly.

- a **configuration file specifying the table and schema names in the database** (*'obia4rtm_backend.cfg'*). Most likely you will only have to change something in there in case you want to use additional database schemes.

- a file that holds the soil spectra. Per default, the **soil spectra** offered by PyProsail are used (*'soil_relfectance.txt'*). However, it is also possible to add a custom soil spectrum in case, for instance, in-situ reference information for a specific region is available. Since the handling of external files is not very convenient it is `**planned to integrate the soil spectra directly into the OBIA4RTM database`**.

- a file specifying the **parameterization of the ProSAIL lookup table(s)** (*'prosail.txt'*) per land use/ cover class. Since the handling of this configuration file is also not very convenient it is planned to change the layout of the file and the way the parameters are set in a future release of the software.

- an additional file mapping the codes and semantic defintion of the **land cover/ land use classes** to be used in OBIA4RTM (*'landcover.cfg*). Whenever you are about to add a new land use/ cover class you have to change the information in this file. Most likely, however, this will be also changed in a future version of the software.

All the files are located in the **`OBIA4RTM home directory`** which can be found in the user directory once OBIA4RTM was successfully installed (see section above). Most often users will want to chnage the ProSAIL configuration file since this file is essential for running the ProSAIL forward simulations and hence the derivation of plant parameters. Please note that the overall structure of the files must be maintained as otherwise I/O-related errors are very likely to occur. Therefore, it might be safer to keep a copy of the original files that came with the installation whenever you are changing something.

### Image Preprocessing

To enable *operational usage* of OBIA4RTM, **preprocessing opportunities** are offered using **`Google Earth Engine (Python API client)`** (GEE) or **`Sen2Core`** software together with **`GDAL`**.

The **Sen2Core** approach is optional in the way that OBIA4RTM also accepts imagery in Level-2A directly provided from ESA (i.e images one which Sen2Core was almost executed by ESA). Using GDAL, the imagery is then also brought in the format required by OBIA4RTM (GeoTiff as image stack of the required Sentinel-2 bands and the SCL layer). Thus, the user has not to take care about any annoying preprocessing or file conversion issues.

The **GEE** approach includes atmospheric correction using **Py6S** as well as cloud and cloud shadow masking using functionalities provided by Sam Murphy under Apache 2.0 license.
Check out

- https://github.com/samsammurphy/gee-atmcorr-S2 for the atmospheric correction algorithm, and

- https://github.com/samsammurphy/cloud-masking-sentinel2 for the cloud and shadow masking

The preprocessed images are then stored and treated the same way in OBIA4RTM as in the file- (Sen2Core) based way.

For demonstration, some sample code is available in a Jupyter Notebook https://github.com/lukasValentin/OBIA4RTM/tree/master/Examples/jupyter

**NOTE**: Please make sure to follow the installation instructions before running this functionality and having the Google Earth Engine client enabled.

### Inversion

The inversion (i.e. derivation of plant biochemical and biophysical parameters) is done numerically since the invserse of the radiative transfer equations is not defined analytically. OBIA4RTM therefore uses a cost function to find the closest match between the satellite-derived and ProSAIL-modelled spectra per land use/cover class. Currently, only the **root mean squared error (RMSE)** is supported as cost function since it is very simple and computational effecient. Future versions of OBIA4RTM might also include additional and more advanced cost functions. To ensure the **numerical stability of the inversion** the user can specify that the average of the best *n* solutions is used in terms of the lowest RMSE. *n* can range between 1 and *N*, where *N* is the number of spectra in the LUT even that makes not really sense from a physical point of view since the average of all spectra in the LUT will most likely not correspond to a physically meaningful solution.


Demodata produced with OBIA4RTM
-------------------------------

Sample data can be found here: http://dx.doi.org/10.17632/vs55cwssyh.1 showing some Sentinel-2 data that was processed using OBIA4RTM in an agricultural area in Southern Germany.

Publications
------------
Lukas Graf, Levente Papp & Stefan Lang (2020) OBIA4RTM – towards an operational open-source solution for coupling object-based image analysis with radiative transfer modelling, European Journal of Remote Sensing, DOI: 10.1080/22797254.2020.1810132

OBIA4RTM
--------
[![DOI](https://zenodo.org/badge/184379375.svg)](https://zenodo.org/badge/latestdoi/184379375)


