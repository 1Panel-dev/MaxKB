SELECT
	COUNT ( "application_public_access_client"."id" ) AS "customer_added_count",
	create_time :: DATE as "day"
FROM
	"application_public_access_client"
${default_sql}
GROUP BY "day"