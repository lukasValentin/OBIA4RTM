-- Table: obia4rtm_sentinel_2.s2_lai_view

-- DROP TABLE obia4rtm_sentinel_2.s2_lai_view;

CREATE TABLE obia4rtm_sentinel_2.s2_lai_view AS 
 SELECT inversion.object_id,
    inversion.acquisition_date,
    (inversion.inversion_results ->> 'cbrown'::text)::double precision AS cbrown,
    (inversion.inversion_results ->> 'lai'::text)::double precision AS lai,
    (inversion.inversion_errors ->> '1'::text)::double precision AS rmse_lowest,
    (inversion.inversion_errors ->> '10'::text)::double precision AS rmse_highest,
    obj_geom.object_geom
   FROM obia4rtm_sentinel_2.s2_inversion_results inversion,
    obia4rtm_sentinel_2.s2_obj_spectra obj_geom
  WHERE inversion.object_id = obj_geom.object_id AND inversion.acquisition_date = obj_geom.acquisition_date;

ALTER TABLE obia4rtm_sentinel_2.s2_lai_view ADD PRIMARY KEY(object_id, acquisition_date);

ALTER TABLE obia4rtm_sentinel_2.s2_lai_view
  OWNER TO postgres;