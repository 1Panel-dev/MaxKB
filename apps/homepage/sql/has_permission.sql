select exists (
    select 1
    from user_role_relation urr
    left join role_permission rp
        on rp.role_id = urr.role_id
    where urr.user_id = %s
      and urr.workspace_id = %s
      and (
          urr.role_id = any (array['USER'])
          or rp.permission_id = %s
      )
) as has_permission;