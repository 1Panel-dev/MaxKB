SELECT
    u.id,
    u.nick_name,
    u.username,
    (case
		when wurp.auth_type = 'ROLE'
		and  'ROLE' = any(wurp.permission_list) then 'ROLE'
			when wurp.auth_type = 'RESOURCE_PERMISSION_GROUP'
			and 'MANAGE'= any(wurp.permission_list)   then 'MANAGE'
			  when wurp.auth_type = 'RESOURCE_PERMISSION_GROUP'
			and 'VIEW' = any(wurp.permission_list) then 'VIEW'
			else 'NOT_AUTH'
		end) as "permission_list"
FROM
    public."user" u
LEFT JOIN (
    SELECT
        *
    FROM
        workspace_user_resource_permission
        ${workspace_user_resource_permission_query_set}
        ) wurp
ON
    u.id = wurp.user_id
${user_query_set}