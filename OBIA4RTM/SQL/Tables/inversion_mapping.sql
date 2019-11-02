--
-- create a table that provides a mapping between the scene_id and the parameters
-- to be retrieved for a given acquisiton date and land use category
-- Lukas Graf, graflukas@web.de
-- 
-- CREATE EXTENSION hstore; -- use JSON extension (must be enabled when running the first time)

CREATE TABLE schema_name.table_name(
	acquisition_date 	DATE NOT NULL,
	params_to_be_inverted 	JSON NOT NULL,
	landuse 		INTEGER,
	sensor 			CHARACTER VARYING(20) DEFAULT 'S2A',
	scene_id 		CHARACTER VARYING(255) NOT NULL,
	CONSTRAINT inv_map_pkey PRIMARY KEY (scene_id, landuse)
);
