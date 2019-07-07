--
-- creates a lookup-table for inverting Sentinel-2 imagery using the ProSAIL model
-- Lukas Graf, graflukas@web.de
--
CREATE TABLE public.s2_lut
(
  id bigint NOT NULL,
  acquisition_date DATE NOT NULL,
  landuse INTEGER DEFAULT 999,
  n double precision,
  cab double precision,
  car double precision,
  cbrown double precision,
  cw double precision,
  cm double precision,
  lai double precision,
  lidfa double precision,
  lidfb double precision,
  rsoil double precision,
  psoil double precision,
  hspot double precision,
  tts double precision,
  tto double precision,
  psi double precision,
  typelidf double precision,
  b2 double precision,
  b3 double precision,
  b4 double precision,
  b5 double precision,
  b6 double precision,
  b7 double precision,
  b8a double precision,
  b11 double precision,
  b12 double precision,
  PRIMARY KEY (id, acquisition_date)
)
WITH (
  OIDS=FALSE
);
