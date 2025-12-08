SELECT *
FROM (SELECT "temp_knowledge".id::text, "temp_knowledge".name,
             "temp_knowledge".desc,
             "temp_knowledge".type,
             'knowledge'                               as resource_type,
             "temp_knowledge".workspace_id,
             "temp_knowledge".folder_id,
             "temp_knowledge".user_id,
             "user"."nick_name"                        as nick_name,
             "temp_knowledge".create_time,
             "temp_knowledge".update_time,
             "temp_knowledge".file_size_limit,
             "temp_knowledge".file_count_limit,
             "temp_knowledge"."scope",
             "temp_knowledge"."embedding_model_id"::text,
             "document_temp"."char_length",
             to_json("temp_knowledge".meta)::jsonb       as meta,
             CASE
                 WHEN
                     "app_knowledge_temp"."count" IS NULL THEN 0
                 ELSE "app_knowledge_temp"."count" END AS application_mapping_count,
             "document_temp".document_count
      FROM (SELECT knowledge.*
            FROM knowledge knowledge ${knowledge_custom_sql}
            AND "knowledge".id::text in (select target
                   from workspace_user_resource_permission
                   ${workspace_user_resource_permission_query_set}
                     and case
                             when auth_type = 'ROLE' then
                                 'ROLE' = any (permission_list)
                                  and
                                 'KNOWLEDGE:READ' in (select (case when user_role_relation.role_id = any (array ['USER']) THEN 'KNOWLEDGE:READ' else role_permission.permission_id END)
                                                        from role_permission role_permission
                                                        right join user_role_relation user_role_relation
                                                            on user_role_relation.role_id=role_permission.role_id
                                                        where user_role_relation.user_id=workspace_user_resource_permission.user_id
                                                        and  user_role_relation.workspace_id=workspace_user_resource_permission.workspace_id)
                             else
                                 'VIEW' = any (permission_list)
                       end
            )) temp_knowledge
               LEFT JOIN (SELECT "count"("id") AS document_count, "sum"("char_length") "char_length", knowledge_id
                          FROM "document"
                          GROUP BY knowledge_id) "document_temp" ON temp_knowledge."id" = "document_temp".knowledge_id
               LEFT JOIN (SELECT "count"("id"), knowledge_id
                          FROM application_knowledge_mapping
                          GROUP BY knowledge_id) app_knowledge_temp
                         ON temp_knowledge."id" = "app_knowledge_temp".knowledge_id
               left join "user" on "user".id = temp_knowledge.user_id
      ) temp
    ${default_sql}