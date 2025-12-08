SELECT
    distinct(u.id),
    u.nick_name,
    u.username,
    case
		when
	      wurp."permission" is null then 'NOT_AUTH'
		else wurp."permission"
	end
FROM
    public."user" u
LEFT JOIN (
    SELECT
        user_id ,
	(case
		when  auth_type = 'ROLE'
		and  'ROLE' = any( permission_list) then 'ROLE'
			when  auth_type = 'RESOURCE_PERMISSION_GROUP'
			and 'MANAGE'= any(permission_list)   then 'MANAGE'
			  when  auth_type = 'RESOURCE_PERMISSION_GROUP'
			and 'VIEW' = any( permission_list) then 'VIEW'
			else null
		end) as "permission"
    FROM
        workspace_user_resource_permission
        ${workspace_user_resource_permission_query_set}
        ) wurp
ON
    u.id = wurp.user_id
left join user_role_relation user_role_relation
on user_role_relation.user_id = u.id
left join role_setting role_setting
on role_setting.id = user_role_relation.role_id
${user_query_set}