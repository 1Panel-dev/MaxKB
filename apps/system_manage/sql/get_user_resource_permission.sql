SELECT app_or_knowledge.*,
      COALESCE(workspace_user_resource_permission.permission_list,'{}')::varchar[] as permission_list,
      COALESCE(workspace_user_resource_permission.auth_type,'ROLE') as auth_type
FROM (SELECT "id",
             "name",
             'KNOWLEDGE' AS "auth_target_type",
             user_id,
             workspace_id,
             "type"::varchar    AS "icon",
             folder_id
      FROM knowledge
      ${knowledge_query_set}
     UNION
     SELECT "id",
             "name",
             'APPLICATION' AS "auth_target_type",
             user_id,
             workspace_id,
             icon,
             folder_id
      FROM application
      ${application_query_set}
      UNION
     SELECT "id",
             "name",
             'TOOL' AS "auth_target_type",
             user_id,
             workspace_id,
             icon,
             folder_id
      FROM tool
      ${tool_query_set}
       UNION
     SELECT "id",
             "name",
             'MODEL' AS "auth_target_type",
             user_id,
             workspace_id,
             provider as icon,
             'default' as folder_id
      FROM model
      ${model_query_set}
   ) app_or_knowledge
         LEFT JOIN (SELECT *
                    FROM workspace_user_resource_permission
                     ${workspace_user_resource_permission_query_set}) workspace_user_resource_permission
                   ON workspace_user_resource_permission.target = app_or_knowledge."id";
