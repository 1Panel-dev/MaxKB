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
        and 'VIEW' = any (permission_list)) ) temp ${model_query_set}
