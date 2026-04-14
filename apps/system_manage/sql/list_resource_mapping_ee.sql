WITH source_data_cte AS (SELECT 'APPLICATION' as source_type,
                                id,
                                "name",
                                "desc",
                                "user_id",
                                "workspace_id",
                                "icon",
                                "type",
                                "folder_id"
                         FROM application
                         UNION ALL
                         SELECT 'KNOWLEDGE' as source_type,
                                id,
                                "name",
                                "desc",
                                "user_id",
                                "workspace_id",
                                "type"::text as "icon" , "type"::text as "type", "folder_id"
                         FROM knowledge
                         UNION ALL
                         SELECT 'TOOL'      as source_type,
                                id,
                                "name",
                                "desc",
                                "user_id",
                                "workspace_id",
                                "icon",
                                "tool_type" as "type",
                                "folder_id"
                         FROM tool)
SELECT rm.*,
       sdc.*,
       u.nick_name as username,
       w.name      as workspace_name
FROM resource_mapping rm
         LEFT JOIN source_data_cte sdc
                   ON rm.source_type = sdc.source_type
                       AND rm.source_id::uuid = sdc.id
         LEFT JOIN "public"."user" u
on u.id = sdc.user_id
    LEFT JOIN "public"."workspace" w on w.id = sdc.workspace_id