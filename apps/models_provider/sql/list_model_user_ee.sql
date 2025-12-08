SELECT *
FROM (SELECT model."id"::text, model."name",
             model.model_name,
             model.meta::json as meta, model.credential,
             model.model_params_form,
             model.model_type,
             model.provider,
             model.status,
             model.create_time,
             model.update_time,
             model.user_id,
             "user"."nick_name" as "nick_name",
             model.workspace_id
      from model
               left join "user" on user_id = "user".id
      where model."id"::text in (select target
                           from workspace_user_resource_permission ${workspace_user_resource_permission_query_set}
        and case
                when auth_type = 'ROLE' then
                    'ROLE' = any (permission_list)
                        and
                    'MODEL:READ' in (select (case
                                                 when user_role_relation.role_id = any (array['USER'])
                                                     THEN 'MODEL:READ'
                                                 else role_permission.permission_id END)
                                     from role_permission role_permission
                                              right join user_role_relation user_role_relation
                                                         on user_role_relation.role_id = role_permission.role_id
                                     where user_role_relation.user_id = workspace_user_resource_permission.user_id
                                       and user_role_relation.workspace_id =
                                           workspace_user_resource_permission.workspace_id)

                else
                    'VIEW' = any (permission_list)
          end) ) temp ${model_query_set}


