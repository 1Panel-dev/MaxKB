SELECT user_group.*, COALESCE(resource_chat_user_group_authorize.is_auth,false) as is_auth
FROM  "user_group"
         LEFT JOIN (SELECT * FROM  resource_chat_user_group_authorize ${resource_chat_user_group_authorize_query_set}) resource_chat_user_group_authorize
                   ON user_group.id = resource_chat_user_group_authorize.user_group_id
${default_query_set}