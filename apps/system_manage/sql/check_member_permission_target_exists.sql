SELECT static_temp."target_id"::text
FROM (SELECT *
      FROM json_to_recordset(
               %s
  ) AS x(target_id text, auth_target_type text)) static_temp
         LEFT JOIN (SELECT id::text AS id,
                           auth_target_type
                    FROM (SELECT "id"::text,
                                 'KNOWLEDGE' AS "auth_target_type"
                          FROM knowledge
                          WHERE workspace_id = %s
                          UNION
                          SELECT "id"::text,
                                 'KNOWLEDGE' AS "auth_target_type"
                          FROM knowledge_folder
                          WHERE workspace_id = %s
                          UNION
                          SELECT "id"::text,
                                 'APPLICATION' AS "auth_target_type"
                          FROM application
                          WHERE workspace_id = %s
                          UNION
                          SELECT "id"::text,
                                 'APPLICATION' AS "auth_target_type"
                          FROM application_folder
                          WHERE workspace_id = %s
                          UNION
                          SELECT "id"::text,
                                 'MODEL' AS "auth_target_type"
                          FROM model
                          WHERE workspace_id = %s
                          UNION
                          SELECT "id"::text,
                                 'TOOL' AS "auth_target_type"
                          FROM tool
                          WHERE workspace_id = %s
                          UNION
                          SELECT "id"::text,
                                 'TOOL' AS "auth_target_type"
                          FROM tool_folder
                          WHERE workspace_id = %s
                          ) "union_temp") "app_and_knowledge_temp"
                   ON "app_and_knowledge_temp"."id" = static_temp."target_id" and
                      app_and_knowledge_temp."auth_target_type" = static_temp."auth_target_type"
WHERE app_and_knowledge_temp.id is NULL;