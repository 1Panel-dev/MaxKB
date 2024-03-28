SELECT
	( SUM ( CASE WHEN create_time :: DATE = CURRENT_DATE THEN 1 ELSE 0 END ) ) AS "customer_today_added_count",
	COUNT ( "application_public_access_client"."id" ) AS "customer_added_count"
FROM
	"application_public_access_client"