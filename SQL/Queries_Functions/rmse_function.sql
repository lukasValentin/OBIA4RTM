--
-- function to calculate the rmse between synthetic (RTM-derived) and satellite spectra
-- using Sentinel-2 data with nine bands
-- created by Lukas Graf on 28th March 2019
--

CREATE  OR REPLACE FUNCTION RMSE(
	b2_sim DOUBLE PRECISION, b3_sim DOUBLE PRECISION, b4_sim DOUBLE PRECISION,
	b5_sim DOUBLE PRECISION, b6_sim DOUBLE PRECISION, b7_sim DOUBLE PRECISION,
	b8a_sim DOUBLE PRECISION, b11_sim DOUBLE PRECISION, b12_sim DOUBLE PRECISION,
	
	b2_sat DOUBLE PRECISION, b3_sat DOUBLE PRECISION, b4_sat DOUBLE PRECISION,
	b5_sat DOUBLE PRECISION, b6_sat DOUBLE PRECISION, b7_sat DOUBLE PRECISION,
	b8a_sat DOUBLE PRECISION, b11_sat DOUBLE PRECISION, b12_sat DOUBLE PRECISION
	
	)

RETURNS DOUBLE PRECISION AS $$
DECLARE
	sql VARCHAR;
	res DOUBLE PRECISION;
BEGIN

	-- function logic
	-- RMSE = SQRT(1/9 * SUM(QUDRATIC_ERROR_FOR_ALL_BANDS))
	
	sql:= 'SELECT SQRT( 1./9. *  (' || 		(b2_sat - b2_sim) * (b2_sat - b2_sim)
						+ 	(b3_sat - b3_sim) * (b3_sat - b3_sim)
						+	(b4_sat - b4_sim) * (b4_sat - b4_sim)
						+	(b5_sat - b5_sim) * (b5_sat - b5_sim)
						+	(b6_sat - b6_sim) * (b6_sat - b6_sim)
						+	(b7_sat - b7_sim) * (b7_sat - b7_sim)
						+	(b8a_sat - b8a_sim) * (b8a_sat - b8a_sim)
						+	(b11_sat - b11_sim) * (b11_sat - b11_sim)
						+	(b12_sat - b12_sim) * (b12_sat - b12_sim)
					||
					'))';
	EXECUTE sql INTO res;
	RETURN res;
	
END;
$$
LANGUAGE plpgsql;


-- usage example
-- SELECT rmse(1.45, 1.45, 1.45, 1.45, 1.45, 1.45, 1.45, 1.45, 1.45,
--	     1.45, 1.45, 1.45, 1.45, 1.45, 1.45, 1.45, 1.45, 1.46);
