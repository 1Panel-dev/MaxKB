SELECT
	( SUM ( CASE WHEN create_time :: DATE = CURRENT_DATE THEN 1 ELSE 0 END ) ) AS "today_added_count",
	COUNT ( "application_public_access_client"."id" ) AS "added_count"
FROM
	"application_public_access_client"