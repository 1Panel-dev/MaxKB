SELECT *
FROM (SELECT tool."id"::text,
             tool."name",
             tool."desc",
             tool."tool_type",
             tool."scope",
             'tool'           AS "resource_type",
             tool."workspace_id",
             tool."folder_id",
             tool."user_id",
             "user".nick_name AS "nick_name",
             tool."icon",
             tool.label,
             tool."template_id"::text,
             tool."create_time",
             tool."update_time",
             tool.init_field_list,
             tool.input_field_list,
             tool.version,
             tool."is_active"
      FROM (SELECT tool.*
            FROM tool tool ${tool_query_set}
             AND tool.id::text IN (SELECT target
                   FROM workspace_user_resource_permission ${workspace_user_resource_permission_query_set}
                AND CASE
                WHEN auth_type = 'ROLE' THEN
                'ROLE' = ANY (permission_list)
                AND
                'TOOL:READ' IN (SELECT (CASE WHEN user_role_relation.role_id = ANY (ARRAY ['USER']) THEN 'TOOL:READ' ELSE role_permission.permission_id END)
                FROM role_permission role_permission
                RIGHT JOIN user_role_relation user_role_relation ON user_role_relation.role_id=role_permission.role_id
                WHERE user_role_relation.user_id=workspace_user_resource_permission.user_id
                AND user_role_relation.workspace_id=workspace_user_resource_permission.workspace_id)
                ELSE
                'VIEW' = ANY (permission_list)
                END
                )) AS tool
               LEFT JOIN "user" ON "user".id = user_id
      ) temp
       ${default_query_set}