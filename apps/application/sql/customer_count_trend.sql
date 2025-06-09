SELECT
	COUNT ( "application_chat_user_stats"."id" ) AS "customer_added_count",
	create_time :: DATE as "day"
FROM
	"application_chat_user_stats"
${default_sql}
GROUP BY "day"