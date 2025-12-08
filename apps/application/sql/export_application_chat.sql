SELECT
    application_chat_record_temp.id AS id,
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
    application_chat_record_temp.create_time as create_time,
    application_chat.asker::json AS asker
FROM
	application_chat application_chat
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
	${default_queryset}