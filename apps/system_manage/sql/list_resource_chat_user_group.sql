SELECT user_group.*, COALESCE(resource_chat_user_group_authorize.is_auth,false) as is_auth,
       (SELECT COUNT(DISTINCT resource_chat_user_authorize.user_id)
        FROM user_group_relation
                 JOIN (SELECT * FROM resource_chat_user_authorize ${resource_chat_user_authorize_query_set}) resource_chat_user_authorize
                      ON resource_chat_user_authorize.user_id = user_group_relation.user_id
                          AND resource_chat_user_authorize.user_group_id = user_group_relation.group_id
        WHERE user_group_relation.group_id = user_group.id
          AND resource_chat_user_authorize.is_auth = true) AS authorized_count
FROM  "user_group"
         LEFT JOIN (SELECT * FROM  resource_chat_user_group_authorize ${resource_chat_user_group_authorize_query_set}) resource_chat_user_group_authorize
                   ON user_group.id = resource_chat_user_group_authorize.user_group_id
${default_query_set}
