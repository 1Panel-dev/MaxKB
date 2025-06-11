SELECT *
FROM (SELECT "temp_knowledge".id::text, "temp_knowledge".name,
             "temp_knowledge".desc,
             "temp_knowledge".type,
             'knowledge'                               as resource_type,
             "temp_knowledge".workspace_id,
             "temp_knowledge".folder_id,
             "temp_knowledge".user_id,
             "temp_knowledge".create_time,
             "temp_knowledge".update_time,
             "temp_knowledge".file_size_limit,
             "temp_knowledge".file_count_limit,
             "temp_knowledge"."scope",
             "document_temp"."char_length",
             CASE
                 WHEN
                     "app_knowledge_temp"."count" IS NULL THEN 0
                 ELSE "app_knowledge_temp"."count" END AS application_mapping_count,
             "document_temp".document_count
      FROM (SELECT knowledge.*
            FROM knowledge knowledge ${knowledge_custom_sql}) temp_knowledge
               LEFT JOIN (SELECT "count"("id") AS document_count, "sum"("char_length") "char_length", knowledge_id
                          FROM "document"
                          GROUP BY knowledge_id) "document_temp" ON temp_knowledge."id" = "document_temp".knowledge_id
               LEFT JOIN (SELECT "count"("id"), knowledge_id
                          FROM application_knowledge_mapping
                          GROUP BY knowledge_id) app_knowledge_temp
                         ON temp_knowledge."id" = "app_knowledge_temp".knowledge_id
      UNION
      SELECT "id",
             "name",
             "desc",
             0           as "type",
             'folder'    as "resource_type",
             "workspace_id",
             "parent_id" as "folder_id",
             "user_id",
             "create_time",
             "update_time",
             0           as file_size_limit,
             0           as file_count_limit,
             'WORKSPACE' as "scope",
             0 as char_length,
                0 as application_mapping_count,
                0 as document_count
      from knowledge_folder ${folder_query_set}) temp
    ${default_sql}