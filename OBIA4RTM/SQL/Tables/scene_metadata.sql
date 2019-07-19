--
-- creates a table for storing scene-specific metadata
-- necessary for retrieving plant parameters from optical satellite data
-- use mean sensor zenith, sun azimuth and relative azimuth angle (deg) for
-- describing the illumination conditions
-- Lukas Graf, graflukas@web.de
--
CREATE TABLE public.scene_metadata(
	scene_id		VARCHAR NOT NULL,			
	acquisition_time 	TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	sun_zenith		DOUBLE PRECISION NOT NULL,	
	obs_zenith		DOUBLE PRECISION NOT NULL,
	rel_azimuth		DOUBLE PRECISION NOT NULL,	
	sensor			CHARACTER VARYING(20) DEFAULT 'SENTINEL-2',
	footprint		GEOMETRY(POLYGON) NOT NULL,			
	full_description	JSON,
	storage_drive		CHARACTER VARYING(2000),
	filename		CHARACTER VARYING(500)			
);
