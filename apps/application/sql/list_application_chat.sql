SELECT
	*,to_json(asker) as asker
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
	WHERE chat_id IN (
	  SELECT id FROM application_chat ${inner_queryset})
	GROUP BY
	application_chat_record.chat_id
	) chat_record_temp ON application_chat."id" = chat_record_temp.chat_id
${default_queryset}