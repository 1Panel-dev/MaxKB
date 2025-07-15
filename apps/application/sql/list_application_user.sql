select *
from (select application."id"::text, application."name",
             application."desc",
             application."is_publish",
             application."type",
             'application'      as "resource_type",
             application."workspace_id",
             application."folder_id",
             application."user_id",
             "user"."nick_name" as "nick_name",
             application."create_time",
             application."update_time",
             application."publish_time",
             application.icon
      from application
               left join "user" on user_id = "user".id
      where application."id" in (select target
                                 from workspace_user_resource_permission ${workspace_user_resource_permission_query_set}
        and 'VIEW' = any (permission_list))
UNION
select application_folder."id",
       application_folder."name",
       application_folder."desc",
       true                           as "is_publish",
       'folder'                       as "type",
       'folder'                       as "resource_type",
       application_folder."workspace_id",
       application_folder."parent_id" as "folder_id",
       application_folder."user_id",
       "user"."nick_name"             as "nick_name",
       application_folder."create_time",
       application_folder."update_time",
       null                           as "publish_time",
       null                           as "icon"
from application_folder
         left join "user" on user_id = "user".id ${folder_query_set}) temp ${application_query_set}