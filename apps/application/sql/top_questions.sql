SELECT COUNT(application_chat_record."id")                         AS chat_record_count,
       MAX(COALESCE(application_chat.asker ->>'username', '游客')) as "username"
FROM application_chat_record application_chat_record
         LEFT JOIN application_chat application_chat ON application_chat."id" = application_chat_record.chat_id
    ${default_sql}
GROUP BY
    application_chat.chat_user_id
ORDER BY
    chat_record_count DESC,
    username ASC

