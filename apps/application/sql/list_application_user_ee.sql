select *
from (select application."id"::text, application."name",
             application."desc",
             application."is_publish",
             application."is_portal",
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
      where "application".id::text in (select target
                                 from workspace_user_resource_permission ${workspace_user_resource_permission_query_set}
        and case
                when auth_type = 'ROLE' then
                    'ROLE' = any (permission_list)
                        and
                    'APPLICATION:READ' in (select (case
                                                       when user_role_relation.role_id = any (array['USER'])
                                                           THEN 'APPLICATION:READ'
                                                       else role_permission.permission_id END)
                                           from role_permission role_permission
                                                    right join user_role_relation user_role_relation
                                                               on user_role_relation.role_id = role_permission.role_id
                                           where user_role_relation.user_id = workspace_user_resource_permission.user_id
                                             and user_role_relation.workspace_id =
                                                 workspace_user_resource_permission.workspace_id)

                else
                    'VIEW' = any (permission_list)
          end
                                 union
                                 select distinct target
                                 from workspace_user_group_resource_permission
                                          inner join system_user_group_relation
                                                     on system_user_group_relation.group_id =
                                                        workspace_user_group_resource_permission.user_group_id
                                 ${workspace_user_group_resource_permission_query_set}
                                   and (
                                           'VIEW' = any (permission_list)
                                           or (
                                                   auth_type = 'ROLE'
                                                   and 'ROLE' = any (permission_list)
                                                   and 'APPLICATION:READ' in (select (case
                                                                                          when user_role_relation.role_id =
                                                                                               any (array['USER'])
                                                                                              then 'APPLICATION:READ'
                                                                                          else
                                                                                              role_permission.permission_id end)
                                                                              from role_permission role_permission
                                                                                       right join user_role_relation user_role_relation
                                                                                                  on user_role_relation.role_id =
                                                                                                     role_permission.role_id
                                                                              where user_role_relation.user_id =
                                                                                    system_user_group_relation.user_id
                                                                                and user_role_relation.workspace_id =
                                                                                    workspace_user_group_resource_permission.workspace_id)
                                           )
                                       ))) temp
${application_query_set}
