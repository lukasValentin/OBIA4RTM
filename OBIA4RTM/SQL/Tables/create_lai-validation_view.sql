-- DROP VIEW obia4rtm_sentinel_2.s2_lai_view;

CREATE OR REPLACE VIEW obia4rtm_sentinel_2.s2_lai_validation AS 
 SELECT inversion.object_id,
    inversion.acquisition_date,
    (inversion.inversion_results ->> 'lai'::text)::double precision AS lai,
    (inversion.inversion_errors ->> '1'::text)::double precision AS rmse_lowest,
    (inversion.inversion_errors ->> '10'::text)::double precision AS rmse_highest,
    in_situ.lai as insitu_lai
   FROM obia4rtm_sentinel_2.s2_inversion_results inversion,
    validation.multiply_lai_2017 in_situ
  WHERE inversion.object_id = in_situ.id
  AND AGE(inversion.acquisition_date, to_date(in_situ.date, 'MM-DD-YYYY')) < '2 days'
  AND AGE(inversion.acquisition_date, to_date(in_situ.date, 'MM-DD-YYYY')) > '-2 days';

ALTER TABLE obia4rtm_sentinel_2.s2_lai_validation
  OWNER TO postgres;