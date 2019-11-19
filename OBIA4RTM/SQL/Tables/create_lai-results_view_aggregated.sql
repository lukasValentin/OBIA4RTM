-- View: validation.s2_lai_validation

-- DROP VIEW validation.s2_lai_validation;

CREATE OR REPLACE VIEW validation.s2_lai_validation AS 
 SELECT inversion.object_id ,
    inversion.acquisition_date,
    AVG((inversion.inversion_results ->> 'lai'::text)::double precision) AS sentinel2_lai,
    AVG(insitu.lai) AS insitu_lai
  FROM obia4rtm_sentinel_2.s2_inversion_results inversion,
    validation.multiply_lai_2017 insitu
  WHERE 
    inversion.object_id = insitu.id
  and
   age(to_date(insitu.date,'MM-DD-YYYY')::DATE, inversion.acquisition_date) > '-2 days'
  and
    age(to_date(insitu.date,'MM-DD-YYYY')::DATE, inversion.acquisition_date) < '2 days'
  AND
    insitu.lai >= 0
  GROUP BY inversion.object_id, inversion.acquisition_date
  ORDER BY acquisition_date;

ALTER TABLE validation.s2_lai_validation
  OWNER TO postgres;
