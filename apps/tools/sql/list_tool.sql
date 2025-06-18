select *
from (select "id"::text,
             "name",
             "desc",
             "tool_type",
             'tool' as "resource_type",
             "workspace_id",
             "folder_id",
             "user_id",
             "icon",
             "create_time",
             "update_time"
      from tool ${tool_scope_query_set}
      UNION
      select "id",
             "name",
             "desc",
             'folder'    as "tool_type",
             'folder'    as "resource_type",
             "workspace_id",
             "parent_id" as "folder_id",
             "user_id",
             '' as "icon",
             "create_time",
             "update_time"
      from tool_folder ${folder_query_set}) temp
    ${tool_query_set}