SELECT COUNT(application_chat_record."id")                          AS chat_record_count,
       COALESCE(application_chat.asker ->>'username', '游客') AS username
FROM application_chat_record application_chat_record
         LEFT JOIN application_chat application_chat ON application_chat."id" = application_chat_record.chat_id
    ${default_sql}
GROUP BY
    COALESCE (application_chat.asker->>'username', '游客')
ORDER BY
    chat_record_count DESC,
    username ASC

