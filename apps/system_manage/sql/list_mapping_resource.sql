WITH target_data_cte AS (SELECT 'APPLICATION' as target_type,
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
                         SELECT 'KNOWLEDGE' as target_type,
                                id,
                                "name",
                                "desc",
                                "user_id",
                                "workspace_id",
                                "type"::text as "icon" , "type"::text as "type", "folder_id"
                         FROM knowledge
                         UNION ALL
                         SELECT 'TOOL'      as target_type,
                                id,
                                "name",
                                "desc",
                                "user_id",
                                "workspace_id",
                                "icon",
                                "tool_type" as "type",
                                "folder_id"
                         FROM tool
                         UNION ALL
                         SELECT 'MODEL'      as target_type,
                                id,
                                "name",
                                ''::text as "desc", "user_id",
                                "workspace_id",
                                "provider"   as "icon",
                                "model_type" as "type",
                                ''::text as "folder_id"
                         FROM model)
SELECT rm.*,
       tdc.*,
       u.nick_name as username
FROM resource_mapping rm
         LEFT JOIN target_data_cte tdc
                   ON rm.target_type = tdc.target_type
                       AND rm.target_id::uuid = tdc.id
LEFT JOIN "public"."user" u
ON u.id = tdc.user_id