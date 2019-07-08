--
-- creates a table for storing scene-specific metadata
-- necessary for retrieving plant parameters from optical satellite data
-- use mean sensor zenith, sun azimuth and relative azimuth angle (deg) for
-- describing the illumination conditions
-- Lukas Graf, graflukas@web.de
--
CREATE TABLE public.scene_metadata(
	acquisition_time 	TIMESTAMP WITHOUT TIME ZONE NOT NULL, 		-- time stamp UTC
	sun_zenith		DOUBLE PRECISION NOT NULL,			-- sun zenith angle (deg)
	obs_zenith		DOUBLE PRECISION NOT NULL,			-- observer (=sensor) zenith angle (deg)
	rel_azimuth		DOUBLE PRECISION NOT NULL,			-- relative azimuth angle (deg)
	sensor			CHARACTER VARYING(20) DEFAULT 'SENTINEL-2',	-- sensor name
	footprint		GEOMETRY(POLYGON) NOT NULL,			-- footprint of the scene coverage
	full_description	JSON,						-- additional metadata extracted from metadata file, optional
	storage_drive		CHARACTER VARYING(2000)				-- physical storage location of the raster file with satellite data
	filename		CHARACTER VARYING(500)				-- filename of the file with satellite data			
);
