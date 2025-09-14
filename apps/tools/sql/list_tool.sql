select *
from (select tool."id"::text,
             tool."name",
             tool."desc",
             tool."tool_type",
             tool."scope",
             'tool'           as "resource_type",
             tool."workspace_id",
             tool."folder_id",
             tool."user_id",
             "user".nick_name as "nick_name",
             tool."icon",
             tool.label,
             tool."template_id"::text,
             tool."create_time",
             tool."update_time",
             tool.init_field_list,
             tool.input_field_list,
             tool.version,
             tool."is_active"
      from tool
               left join "user" on "user".id = user_id ${tool_query_set}
      UNION
      select tool_folder."id",
             tool_folder."name",
             tool_folder."desc",
             'folder'                as "tool_type",
             ''                      as scope,
             'folder'                as "resource_type",
             tool_folder."workspace_id",
             tool_folder."parent_id" as "folder_id",
             tool_folder."user_id",
             "user".nick_name        as "nick_name",
             ''                      as "icon",
             ''                      as label,
             ''                      as "template_id",
             tool_folder."create_time",
             tool_folder."update_time",
             '[]'::jsonb             as init_field_list,
             '[]'::jsonb             as input_field_list,
             ''                      as version,
             'true'                  as "is_active"
      from tool_folder
               left join "user" on "user".id = user_id ${folder_query_set}) temp
     ${default_query_set}