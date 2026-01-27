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
                         SELECT 'TOOL'            as source_type,
                                id,
                                "name",
                                "desc",
                                "user_id",
                                "workspace_id",
                                "icon",
                                "tool_type"::text as "type",
                                "folder_id"
                         FROM tool)
select ett.*,
       ett.meta::json as meta,
       sdc.name as source_name,
       sdc.icon as source_icon,
       sdc.type as type
from event_trigger_task_record ett
         left join source_data_cte sdc
                   on ett.source_id = sdc.id and ett.source_type = sdc.source_type
