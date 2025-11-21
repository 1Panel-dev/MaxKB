
SELECT
    SUM(application_chat_record.message_tokens + application_chat_record.answer_tokens) as "token_usage",
    COALESCE(application_chat.asker->>'username', '游客') as "username"
FROM
    application_chat_record application_chat_record
    LEFT JOIN application_chat application_chat ON application_chat."id" = application_chat_record.chat_id
${default_sql}
GROUP BY
    COALESCE(application_chat.asker->>'username', '游客')
ORDER BY
    "token_usage" DESC
