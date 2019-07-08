--
-- creates a table for storing the image objects and their Sentinel-2 derived reflectance values
-- object geometries are given for each object and each aqusition date to allow for temporal changes
-- Lukas Graf, graflukas@web.de
--
CREATE TABLE obia4rtm_xx.s2_obj_spec
(
  	object_id 		BIGINT NOT NULL,			-- object_id (foreign key together with acquisition date to results table)
  	acquisition_date 	DATE NOT NULL,				-- acquisition date
	scene_id		JSON					-- JSON structure containing the scenes contributing to an object
  	landuse 		INTEGER DEFAULT 999,			-- land cover at given date -> links to land cover table
	object_geom 		GEOMETRY(MultiPolygon) NOT NULL,	-- object geometry at given date
  	b2 			DOUBLE PRECISION,			-- averaged per object reflectance Sentinel-2 band 2 (%)
  	b3 			DOUBLE PRECISION,			-- averaged per object reflectance Sentinel-2 band 3 (%)
  	b4 			DOUBLE PRECISION,			-- averaged per object reflectance Sentinel-2 band 4 (%)
  	b5 			DOUBLE PRECISION,			-- averaged per object reflectance Sentinel-2 band 5 (%)
  	b6 			DOUBLE PRECISION,			-- averaged per object reflectance Sentinel-2 band 6 (%)
  	b7 			DOUBLE PRECISION,			-- averaged per object reflectance Sentinel-2 band 7 (%)
  	b8a 			DOUBLE PRECISION,			-- averaged per object reflectance Sentinel-2 band 8A (%)
  	b11 			DOUBLE PRECISION,			-- averaged per object reflectance Sentinel-2 band 11 (%)
  	b12 			DOUBLE PRECISION,			-- averaged per object reflectance Sentinel-2 band 12 (%)
  	CONSTRAINT s2_objspec_pkey PRIMARY KEY (object_id, acquisition_date)
)
WITH (
  OIDS=FALSE
);

