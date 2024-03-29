SELECT SUM
	( CASE WHEN application_chat_record.vote_status = '0' THEN 1 ELSE 0 END ) AS "star_num",
	SUM ( CASE WHEN application_chat_record.vote_status = '1' THEN 1 ELSE 0 END ) AS "trample_num",
	SUM ( application_chat_record.message_tokens + application_chat_record.answer_tokens ) as "tokens_num",
	"count"(application_chat_record."id") as chat_record_count,
	"count"(DISTINCT application_chat.client_id) customer_num,
	application_chat_record.create_time :: DATE as "day"
FROM
	application_chat_record application_chat_record
	LEFT JOIN application_chat application_chat ON application_chat."id" = application_chat_record.chat_id
${default_sql}
GROUP BY "day"