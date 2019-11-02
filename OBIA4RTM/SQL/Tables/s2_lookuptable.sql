--
-- creates a lookup-table (LUT) for inverting Sentinel-2 imagery using the ProSAIL model
-- allows for storage of multidate lookup-tables 
-- Lukas Graf, graflukas@web.de
--
CREATE TABLE schema_name.table_name
(
	id 			BIGINT NOT NULL, 
  	acquisition_date 	DATE NOT NULL,
	scene_id		CHARACTER VARYING NOT NULL,
  	landuse 		INTEGER DEFAULT 999,
  -- ProSAIL parameters
   --n := mesophyll structure parameter N (-)
   --cab := leaf chlorophyll a+b content (ug/cm²)
  -- car := leaf carotinoid content (ug/cm²)	
  -- cbrown = fraction of brown leaves (-)
  -- cw := leaf equivalent water thickness (cm)
  -- cm := leaf dry matter content (g/cm²)
  -- lai := leaf area index (m²/m²)
  -- lidfa, lidfb := leaf angle distribution parameters
  -- rsoil, psoil := soil brightness parameters
  -- hspot : = hot spot parameter (-)
  -- tts = solar zenith angle (deg)
  -- tto = observer zenith angle (deg)
  -- psi = relative azimuth (deg)
  -- typelidf = type of leaf angle distribution function (instead of lidfa, lidfb)
  -- b2 - b12 = ProSAIL simulated surface reflectance (%)
  	n 			DOUBLE PRECISION,
  	cab 			DOUBLE PRECISION,
  	car 			DOUBLE PRECISION,
  	cbrown 			DOUBLE PRECISION,
  	cw 			DOUBLE PRECISION,
  	cm 			DOUBLE PRECISION,
  	lai 			DOUBLE PRECISION,
  	lidfa 			DOUBLE PRECISION,
  	lidfb 			DOUBLE PRECISION,
  	rsoil 			DOUBLE PRECISION,
  	psoil 			DOUBLE PRECISION,
 	hspot 			DOUBLE PRECISION,
  -- viewing and illumination angles (deg)
  	tts 			DOUBLE PRECISION,
  	tto 			DOUBLE PRECISION,
  	psi 			DOUBLE PRECISION,
  	typelidf 		DOUBLE PRECISION,
  -- simulated Sentinel-2 reflectance values (%)
  	b2 			DOUBLE PRECISION,
  	b3 			DOUBLE PRECISION,
  	b4 			DOUBLE PRECISION,
  	b5 			DOUBLE PRECISION,
  	b6 			DOUBLE PRECISION,
  	b7 			DOUBLE PRECISION,
  	b8a 			DOUBLE PRECISION,
  	b11 			DOUBLE PRECISION,
  	b12 			DOUBLE PRECISION,
  -- set primary key
  	PRIMARY KEY (id, scene_id, landuse)
)
WITH (
  OIDS=FALSE
);
