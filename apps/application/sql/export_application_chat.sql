SELECT
	application_chat."id" as chat_id,
    application_chat.abstract as abstract,
    application_chat_record_temp.problem_text as problem_text,
    application_chat_record_temp.answer_text as answer_text,
    application_chat_record_temp.message_tokens as message_tokens,
    application_chat_record_temp.answer_tokens as answer_tokens,
    application_chat_record_temp.run_time as run_time,
    application_chat_record_temp.details::JSON as details,
    application_chat_record_temp."index" as "index",
    application_chat_record_temp.improve_paragraph_list  as improve_paragraph_list,
    application_chat_record_temp.vote_status as vote_status,
    application_chat_record_temp.create_time as create_time
FROM
	application_chat application_chat
	LEFT JOIN (
	SELECT COUNT
		( "id" ) AS chat_record_count,
		SUM ( CASE WHEN "vote_status" = '0' THEN 1 ELSE 0 END ) AS star_num,
		SUM ( CASE WHEN "vote_status" = '1' THEN 1 ELSE 0 END ) AS trample_num,
		SUM ( CASE WHEN array_length( application_chat_record.improve_paragraph_id_list, 1 ) IS NULL THEN 0 ELSE array_length( application_chat_record.improve_paragraph_id_list, 1 ) END ) AS mark_sum,
		chat_id
	FROM
		application_chat_record
	GROUP BY
		application_chat_record.chat_id
	) chat_record_temp ON application_chat."id" = chat_record_temp.chat_id
	LEFT JOIN (
	SELECT
		*,
	CASE
			WHEN array_length( application_chat_record.improve_paragraph_id_list, 1 ) IS NULL THEN
			'{}' ELSE ( SELECT ARRAY_AGG ( row_to_json ( paragraph ) ) FROM paragraph WHERE "id" = ANY ( application_chat_record.improve_paragraph_id_list ) )
		END as improve_paragraph_list
		FROM
		application_chat_record application_chat_record
	) application_chat_record_temp ON application_chat_record_temp.chat_id = application_chat."id"