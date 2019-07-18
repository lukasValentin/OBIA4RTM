--
-- create a table that provides a mapping between the scene_id and the parameters
-- to be retrieved for a given acquisiton date and land use category
-- Lukas Graf, graflukas@web.de
-- 
CREATE EXTENSION hstore; -- use HSTORE extension (must be enabled when running the first time)

CREATE TABLE obia4rtm_xx.inversion_mapping (
	acquisition_date 	DATE NOT NULL,					-- acquisition date
	params_to_be_inverted 	HSTORE,						-- parameters to be inverted from a given LUT and given land-use class
	lookup_table		CHARACTER VARYING(255) NOT NULL,		-- LUT with the synthetic spectra (table name)
	landuse 		INTEGER NOT NULL,				-- land cover code
	sensor 			CHARACTER VARYING(20) DEFAULT 'SENTINEL-2',	-- sensor name
	scene_id 		CHARACTER VARYING(255) NOT NULL			-- scene id -> links (foreign key) to metadata table
);
