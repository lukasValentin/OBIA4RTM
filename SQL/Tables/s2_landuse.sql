--
-- create a table for storing the land use classes and their semantics (optional)
-- Lukas Graf, graflukas@web.de
--
CREATE TABLE s2_landuse(
	landuse INTEGER UNIQUE NOT NULL,
	landuse_semantic CHARACTER VARYING(50),
	CONSTRAINT s2_landuse_pkey PRIMARY KEY (landuse)
);

-- insert the land use classes and their meaning (Example)
-- INSERT INTO s2_landuse(landuse, landuse_semantic) VALUES (1, 'VEGETATION');
-- INSERT INTO s2_landuse(landuse, landuse_semantic) VALUES (2, 'BARE SOIL');
