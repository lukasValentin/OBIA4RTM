--
-- query to apply the RMSE cost function for inverting a given object
-- can be also used pixel-based
-- Lukas Graf, graflukas@web.de
--
SELECT 
	lut.id,
	rmse(obj.b2, obj.b3, obj.b4, obj.b5, obj.b6, obj.b7, obj.b8a, obj.b11, obj.b12,
		 lut.b2, lut.b3, lut.b4, lut.b5, lut.b6, lut.b7, lut.b8a, lut.b11, lut.b12) as rmse
FROM
	s2_obj_spec as obj,
	s2_lut as lut
WHERE
	obj.object_id = 34 			-- insert the desired object-id here
and
	obj.acquisition_date = '2017-07-31' 	-- insert the specific acquisition date here
and
	obj.landuse = lut.landuse
and
	obj.acquisition_date = lut.acquisition_date
and
	obj.landuse = 1 			-- insert the desired land-use category here
and
	rmse(obj.b2, obj.b3, obj.b4, obj.b5, obj.b6, obj.b7, obj.b8a, obj.b11, obj.b12,
		 lut.b2, lut.b3, lut.b4, lut.b5, lut.b6, lut.b7, lut.b8a, lut.b11, lut.b12) < 15

order by rmse
LIMIT 10;					-- return the e.g. 10 ten best results
