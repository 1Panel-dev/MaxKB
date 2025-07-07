SELECT COUNT
		( "id" ) AS chat_record_count,
		SUM ( CASE WHEN "vote_status" = '0' THEN 1 ELSE 0 END ) AS star_num,
		SUM ( CASE WHEN "vote_status" = '1' THEN 1 ELSE 0 END ) AS trample_num,
		SUM ( CASE WHEN array_length( application_chat_record.improve_paragraph_id_list, 1 ) IS NULL THEN 0 ELSE array_length( application_chat_record.improve_paragraph_id_list, 1 ) END ) AS mark_sum
FROM
		application_chat_record