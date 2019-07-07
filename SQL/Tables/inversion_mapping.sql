--
-- create a table that provides a mapping between the scene_id and the parameters
-- to be retrieved for a given acquisiton date and land use category
-- Lukas Graf, graflukas@web.de
-- 
CREATE EXTENSION hstore; -- use HSTORE extension (must be enabled when running the first time)

CREATE TABLE inversion_mapping (
	acquisition_date DATE NOT NULL,
	params_to_be_inverted HSTORE,
	landuse INTEGER NOT NULL,
	sensor CHARACTER VARYING(20) DEFAULT 'SENTINEL-2',
	scene_id INTEGER NOT NULL
);
