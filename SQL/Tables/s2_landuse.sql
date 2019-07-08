--
-- create a table for storing the land use classes and their semantics (optional)
-- Lukas Graf, graflukas@web.de
--
CREATE TABLE public.s2_landuse(
	landuse 		INTEGER UNIQUE NOT NULL,	-- land cover code
	landuse_semantic 	CHARACTER VARYING(50),		-- semantic description of land cover code
	CONSTRAINT s2_landuse_pkey PRIMARY KEY (landuse)	-- primary key -> codes must be unique
);

-- insert the land use classes and their meaning (Example)
-- INSERT INTO public.s2_landuse(landuse, landuse_semantic) VALUES (1, 'VEGETATION');
-- INSERT INTO public.s2_landuse(landuse, landuse_semantic) VALUES (2, 'BARE SOIL');
