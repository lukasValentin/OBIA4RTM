--
-- creates a lookup-table (LUT) for inverting Sentinel-2 imagery using the ProSAIL model
-- allows for storage of multidate lookup-tables 
-- Lukas Graf, graflukas@web.de
--
CREATE TABLE obia4rtm_xx.s2_lut
(
	id 			BIGINT NOT NULL, 	-- ID must be unique for each entry in the lookup-table
  	acquisition_date 	DATE NOT NULL,		-- date of scene acquisition
  	landuse 		INTEGER DEFAULT 999,	-- land cover code, if 999, no land cover classification is specified
  -- ProSAIL parameters
  	n 			DOUBLE PRECISION,	-- mesophyll structure parameter N (-)	
  	cab 			DOUBLE PRECISION,	-- leaf chlorophyll a+b content (ug/cm²)
  	car 			DOUBLE PRECISION,	-- leaf carotinoid content (ug/cm²)	
  	cbrown 			DOUBLE PRECISION,	-- fraction of brown leaves (-)
  	cw 			DOUBLE PRECISION,	-- leaf equivalent water thickness (cm)
  	cm 			DOUBLE PRECISION,	-- leaf dry matter content (g/cm²)
  	lai 			DOUBLE PRECISION,	-- leaf area index (m²/m²)
  	lidfa 			DOUBLE PRECISION,	-- leaf angle distribution parameter a (-)
  	lidfb 			DOUBLE PRECISION,	-- leaf angle distribution parameter b (-)
  	rsoil 			DOUBLE PRECISION,	-- soil brightness parameter r (-)
  	psoil 			DOUBLE PRECISION,	-- soil brightness parameter p (-)
 	hspot 			DOUBLE PRECISION,	-- hot spot parameter (-)
  -- viewing and illumination angles (deg)
  	tts 			DOUBLE PRECISION,	-- solar zenith angle (deg) -> from scene metadata
  	tto 			DOUBLE PRECISION,	-- observer (=sensor) zenith angle (deg) -> from scene metadata
  	psi 			DOUBLE PRECISION,	-- relative azimuth angle (deg) -> between sun and sensor
  	typelidf 		DOUBLE PRECISION,	-- type of leaf distribution function
  -- simulated Sentinel-2 reflectance values (%)
  	b2 			DOUBLE PRECISION,	-- Sentinel-2 Band 2 (%)
  	b3 			DOUBLE PRECISION,	-- Sentinel-2 Band 3 (%)
  	b4 			DOUBLE PRECISION,	-- Sentinel-2 Band 4 (%)
  	b5 			DOUBLE PRECISION,	-- Sentinel-2 Band 5 (%)
  	b6 			DOUBLE PRECISION,	-- Sentinel-2 Band 6 (%)
  	b7 			DOUBLE PRECISION,	-- Sentinel-2 Band 7 (%)
  	b8a 			DOUBLE PRECISION,	-- Sentinel-2 Band 8A (%)
  	b11 			DOUBLE PRECISION,	-- Sentinel-2 Band 11 (%)
  	b12 			DOUBLE PRECISION,	-- Sentinel-2 Band 12 (%)
  -- set primary key
  	PRIMARY KEY (id, acquisition_date)
)
WITH (
  OIDS=FALSE
);
