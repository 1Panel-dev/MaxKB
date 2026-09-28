SELECT chat_user.id, chat_user.username, chat_user.nick_name, chat_user.is_active,
       chat_user.source, chat_user.create_time,
       COALESCE(resource_chat_user_authorize.is_auth, false) AS is_auth
FROM chat_user
         LEFT JOIN user_group_relation
                   ON chat_user.id = user_group_relation.user_id

         LEFT JOIN (SELECT *
                    FROM resource_chat_user_authorize ${resource_chat_user_authorize_query_set}) AS resource_chat_user_authorize
                   ON chat_user.id = resource_chat_user_authorize.user_id
                       AND resource_chat_user_authorize.user_group_id = user_group_relation.group_id
    ${default_query_set}
