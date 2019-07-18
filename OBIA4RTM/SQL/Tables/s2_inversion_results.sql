--
-- creates a table for storing the results of the inversion procedure
-- uses a hybrid approach (relational + object-oriented) to allow for maximum
-- flexibility and compability with future changes and add-ons of the tool
-- Lukas Graf, graflukas@web.de
--
CREATE TABLE obia4rtm_xx.s2_inversion_results(
	object_id 		BIGINT NOT NULL,	-- id of the object for which parameters were derived (together with acquisition date foreign key to object table)
	acquisition_date 	DATE NOT NULL,		-- acquisition date for which parameters are valid (together wiht id foreign key to object table)
	scene_id		CHARACTER VARYING(255)  -- scene ID -> foreign key to inversion mapping table specifying the parameters to be inverted and scene metadata link
				NOT NULL
	inversion_results 	JSON,			-- results of inversion as JSON (allows for high degree of flexibility)
	inversion_errors 	JSON,			-- spectral residues (errors) of the closest match between simulated and observed spectra (quality indicator)
	CONSTRAINT s2_obj_inversion_pkey PRIMARY KEY(object_id, acquisition_date)
);
	
