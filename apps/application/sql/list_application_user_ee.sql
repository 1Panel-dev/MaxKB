select *
from (select application."id"::text,
             application."name",
             application. "desc",
             application. "is_publish",
             application."type",
             'application' as "resource_type",
             application."workspace_id",
             application. "folder_id",
             application."user_id",
             "user"."nick_name" as "nick_name",
             application."create_time",
             application."update_time"
      from application left join "user" on user_id = "user".id
      where id in (select target
                   from workspace_user_resource_permission
                   where auth_target_type = 'APPLICATION'
                     and case
                             when auth_type = 'ROLE' then
                                 'APPLICATION_READ' in (select permission_id
                                                        from role_permission
                                                        where role_id in (select role_id
                                                                          from user_role_relation))
                             else
                                 'VIEW' = any (permission_list)
                       end)
      UNION
      select application_folder."id",
             application_folder."name",
             application_folder."desc",
             true  as "is_publish",
             'folder' as "type",
             'folder' as "resource_type",
             application_folder."workspace_id",
             application_folder."parent_id" as  "folder_id",
             application_folder."user_id",
             "user"."nick_name" as "nick_name",
             application_folder."create_time",
             application_folder."update_time"
      from application_folder left join "user" on user_id = "user".id ${folder_query_set}) temp
${application_query_set}