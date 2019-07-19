--
-- SQL script to create and populate a table holding the sensor specific metadata in terms
-- of sensor name, band alias, band number, central wavelength (nm) and band width (nm)
-- Sentinel-2A and 2B are currently supported by default; new sensors (e.g. Landsat-8 OLI) can
-- be added in according manner
-- Lukas Graf, graflukas@web.de
--
CREATE TABLE public.s2_bands
(
  	sensor 		CHARACTER VARYING(10) NOT NULL,		
  	band_alias 	CHARACTER VARYING(10),			
  	band_number 	CHARACTER VARYING(10) NOT NULL,		
  	central_wvl 	DOUBLE PRECISION NOT NULL,		
  	band_width 	DOUBLE PRECISION NOT NULL,		
  	CONSTRAINT s2_bands_pkey PRIMARY KEY (sensor, band_number)
)
WITH (
  OIDS=FALSE
);

-- BANDS AS PROVIDED BY ESA (https://sentinel.esa.int/web/sentinel/user-guides/sentinel-2-msi/resolutions/radiometric)
-- assessed on 25th March 2019

-- Sentinel-2A -> populate the table
INSERT INTO public.s2_bands (sensor, band_alias, band_number, central_wvl, band_width) VALUES('S2A', 'BLUE', '2', 492.4, 98.);
INSERT INTO public.s2_bands (sensor, band_alias, band_number, central_wvl, band_width) VALUES('S2A', 'GREEN', '3', 559.8, 45.);
INSERT INTO public.s2_bands (sensor, band_alias, band_number, central_wvl, band_width) VALUES('S2A', 'RED', '4', 664.6, 38.);
INSERT INTO public.s2_bands (sensor, band_alias, band_number, central_wvl, band_width) VALUES('S2A', 'RED-EDGE 1', '5', 704.1, 19.);
INSERT INTO public.s2_bands (sensor, band_alias, band_number, central_wvl, band_width) VALUES('S2A', 'RED-EDGE 2', '6', 740.5, 18.);
INSERT INTO public.s2_bands (sensor, band_alias, band_number, central_wvl, band_width) VALUES('S2A', 'NIR 1', '7', 782.8, 28.);
INSERT INTO public.s2_bands (sensor, band_alias, band_number, central_wvl, band_width) VALUES('S2A', 'NIR 2', '8a', 864.7, 33.);
INSERT INTO public.s2_bands (sensor, band_alias, band_number, central_wvl, band_width) VALUES('S2A', 'SWIR 1', '11', 1613.7, 143.);
INSERT INTO public.s2_bands (sensor, band_alias, band_number, central_wvl, band_width) VALUES('S2A', 'SWIR 2', '12', 2204.4, 242.);

-- Sentinel-2B -> populate the table
INSERT INTO public.s2_bands (sensor, band_alias, band_number, central_wvl, band_width) VALUES('S2B', 'BLUE', '2', 492.1, 98.);
INSERT INTO public.s2_bands (sensor, band_alias, band_number, central_wvl, band_width) VALUES('S2B', 'GREEN', '3', 559.0, 46.);
INSERT INTO public.s2_bands (sensor, band_alias, band_number, central_wvl, band_width) VALUES('S2B', 'RED', '4', 664.9, 39.);
INSERT INTO public.s2_bands (sensor, band_alias, band_number, central_wvl, band_width) VALUES('S2B', 'RED-EDGE 1', '5', 703.8, 20.);
INSERT INTO public.s2_bands (sensor, band_alias, band_number, central_wvl, band_width) VALUES('S2B', 'RED-EDGE 2', '6', 739.1, 18.);
INSERT INTO public.s2_bands (sensor, band_alias, band_number, central_wvl, band_width) VALUES('S2B', 'NIR 1', '7', 779.7, 28.);
INSERT INTO public.s2_bands (sensor, band_alias, band_number, central_wvl, band_width) VALUES('S2B', 'NIR 2', '8a', 864.0, 32.);
INSERT INTO public.s2_bands (sensor, band_alias, band_number, central_wvl, band_width) VALUES('S2B', 'SWIR 1', '11', 1610.4, 141.);
INSERT INTO public.s2_bands (sensor, band_alias, band_number, central_wvl, band_width) VALUES('S2B', 'SWIR 2', '12', 2185.7, 238.);
