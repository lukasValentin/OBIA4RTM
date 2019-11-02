--
-- creates a table for storing the results of the inversion procedure
-- uses a hybrid approach (relational + object-oriented) to allow for maximum
-- flexibility and compability with future changes and add-ons of the tool
-- Lukas Graf, graflukas@web.de
--
CREATE TABLE schema_name.table_name(
	object_id 		BIGINT NOT NULL,
	acquisition_date 	DATE NOT NULL,
	scene_id		CHARACTER VARYING(255) NOT NULL,
	inversion_results 	JSON,
	inversion_errors 	JSON,
	CONSTRAINT s2_obj_inversion_pkey PRIMARY KEY(object_id, scene_id)
);
