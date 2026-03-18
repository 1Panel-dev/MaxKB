SELECT
    application_chat.*,
    to_json(application_chat.asker) AS asker,
    chat_record_temp.chat_record_count,
    chat_record_temp.star_num,
    chat_record_temp.trample_num,
    chat_record_temp.mark_sum
FROM application_chat
LEFT JOIN (
    SELECT
        application_chat_record.chat_id,
        COUNT(application_chat_record.id) AS chat_record_count,
        SUM((application_chat_record.vote_status = '0')::int) AS star_num,
        SUM((application_chat_record.vote_status = '1')::int) AS trample_num,
        SUM(COALESCE(array_length(application_chat_record.improve_paragraph_id_list, 1), 0)) AS mark_sum
    FROM application_chat_record
    JOIN application_chat application_chat ON application_chat.id = application_chat_record.chat_id
    ${inner_queryset}
    GROUP BY application_chat_record.chat_id
) chat_record_temp ON application_chat.id = chat_record_temp.chat_id
${default_queryset}