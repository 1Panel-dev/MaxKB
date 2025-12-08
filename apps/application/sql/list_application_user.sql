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
      where application."id"::text in (select target
                                 from workspace_user_resource_permission ${workspace_user_resource_permission_query_set}
        and 'VIEW' = any (permission_list))) temp
${application_query_set}