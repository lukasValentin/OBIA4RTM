--
-- creates a database for the OBIA4RTM backend
-- Lukas Graf, graflukas@web.de
--
CREATE DATABASE OBIA4RTM
  WITH OWNER = postgres
       ENCODING = 'UTF8'
       TABLESPACE = pg_default
       LC_COLLATE = 'en_US.UTF-8'
       LC_CTYPE = 'en_US.UTF-8'
       CONNECTION LIMIT = -1;
