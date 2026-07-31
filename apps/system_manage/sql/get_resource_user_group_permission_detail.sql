SELECT
    u.id,
    u.name,
    case
		when
	      wurp."permission" is null then 'NOT_AUTH'
		else wurp."permission"
	end
FROM
    public."system_user_group" u
LEFT JOIN (
    SELECT
        user_group_id ,
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
        workspace_user_group_resource_permission
        ${workspace_user_group_resource_permission_query_set}
        ) wurp
ON
    u.id = wurp.user_group_id
${user_query_set}