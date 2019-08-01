--
-- creates a table for storing the image objects and their Sentinel-2 derived reflectance values
-- object geometries are given for each object and each aqusition date to allow for temporal changes
-- Lukas Graf, graflukas@web.de
--
CREATE TABLE schema_name.table_name
(
  	object_id 		BIGINT NOT NULL,
  	acquisition_date 	DATE NOT NULL,
	scene_id		CHARACTER VARYING NOT NULL,
  	landuse 		INTEGER DEFAULT 999,	
	object_geom 		GEOMETRY(MultiPolygon) NOT NULL,	
  	b2 			DOUBLE PRECISION,
  	b3 			DOUBLE PRECISION,
  	b4 			DOUBLE PRECISION,
  	b5 			DOUBLE PRECISION,
  	b6 			DOUBLE PRECISION,
  	b7 			DOUBLE PRECISION,
  	b8a 			DOUBLE PRECISION,
  	b11 			DOUBLE PRECISION,
  	b12 			DOUBLE PRECISION,
  	CONSTRAINT s2_objspec_pkey PRIMARY KEY (object_id, scene_id)
)
WITH (
  OIDS=FALSE
);

