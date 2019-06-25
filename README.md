**OBIA4RTM**
------------
[![DOI](https://zenodo.org/badge/184379375.svg)](https://zenodo.org/badge/latestdoi/184379375)

An open-source tool for object-based image analysis for radiative transfer modeling
using ProSAIL (Prospect5 + 4SAIL).

**IMPORTANT**	OBIA4RTM is currently just a first prototype and by **no means** a ready-to-use Python package. Updates will follow in the near future.

About OBIA4RTM
--------------

OBIA4RTM aims for **`plant parameter retrieval`** - relevant in *smart farming* applications - by using **`radiative transfer models (RTM)`** and **`object-based image analysis (OBIA)`** that
direclty addresses actual user needs and policy demands in a highly efficient, flexible and scalable way. It uses optical satellite data (concurrently **Sentinel-2**) as input.

The RTM approach makes the tool transferable and nearly globally applicable to a broad range of different crop types, while OBIA accounts for producing results on a per-object rather than per pixel-base. Image objects have the distinct advantage of being directly related to real-world entities such as single field parcels. Furthermore, results on a per-object base can be easily managed and shared via geospatial databases and web-interfaces and refer also to the requirements of the Big-Data era.

The basis idea of OBIA4RTM is to combine to widely used Remote Sensing analysis techniques:

The biophysical parameter retrieval from optical imagery by means of radiative transfer modelling (RTM) and the object-based image analysis (OBIA) concept. While RTM accounts for retrieving the most relevant plant parameters relevant in farming context (Leaf Area Index, Leaf Chlorophyll Content, etc.), the OBIA approach allows for semantic enrichment of spectral data by means of **incorporating expert knowledge and advanced spatial analysis techniques**.

OBIA4RTM relies therefore on two main pillars: It describes plant spectra by means of physical equations that are universally applicable by using RTM and it introduces the concept of spatial autocorrelation to reduce redundancies and provide more meaningful image objects by means of OBIA. It is thereby capable to provide vegetation parameter retrieval techniques that are not bound by temporal or geographic restrictions. Furthermore, **OBIA4RTM directly addresses objects and, thus, human needs** as humans tend not to think in artificial spatial units (i.e. pixels)
but in terms of tangible entities such as single field patches or individual trees in an orchard.

Workflow
--------

The overall workflow implemented in OBIA4RTM is shown below.

![OBIA4RTM Workflow](https://github.com/lukasValentin/OBIA4RTM/OBIA4RTM_Workflow.gif "OBIA4RTM Workflow Overview")


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

- In the future, an xml-file containing the metadata of the Sen2Core Level-2A can be supplied that will be used for retrieving illumination and geometry metadata required for creating the ProSAIL LUT. As long as this feature is not ready (or no Sen2Core like xml metadata is available), this information needs to be inserted manually.

- the use of Copernicus land monitoring data is just a *suggestion*. Users can use also different land cover/ use classification or can even provide no classification at all (then all objects will be treated equally, otherwise, vegetation parameters have to be set per land use class).

- OBIA4RTM does not provide any image segementation facilities as there are lots of freely available image segmentation algorithms available (e.g. within the **Orfeo-Toolbox**).

- concurrently, OBIA4RTM uses the Root Mean Squared Error (RMSE) as cost function within the inversion strategy. Users can specify their own cost-functions. It is planned to add more cost functions in the future.

- all image objects are stored in a PostgreSQL database with PostGIS extension. Make sure to have PostgreSQL **and** PostGIS installed on your machine or where-ever you want to run OBIA4RTM.


Demodata produced with OBIA4RTM
-------------------------------

Sample data can be found here: http://dx.doi.org/10.17632/vs55cwssyh.1 showing some Sentinel-2 data that was processed using OBIA4RTM in an agricultural area in Southern Germany.

OBIA4RTM
--------
[![DOI](https://zenodo.org/badge/184379375.svg)](https://zenodo.org/badge/latestdoi/184379375)

