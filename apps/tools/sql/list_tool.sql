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
      ) temp
     ${default_query_set}