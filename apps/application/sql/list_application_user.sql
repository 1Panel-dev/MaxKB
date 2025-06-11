select *
from (select "id"::text,
             "name",
             "desc",
             "is_publish",
             "type",
             'application' as "resource_type",
             "workspace_id",
             "folder_id",
             "user_id",
             "create_time",
             "update_time"
      from application
      where id in (select target
                   from workspace_user_resource_permission
                   where auth_target_type = 'APPLICATION'
                     and 'VIEW' = any (permission_list))
      UNION
      select "id",
             "name",
             "desc",
              true  as "is_publish",
             'folder' as "type",
             'folder' as "resource_type",
              "workspace_id",
              "parent_id" as  "folder_id",
             "user_id",
             "create_time",
             "update_time"
      from application_folder ${folder_query_set}) temp
${application_query_set}