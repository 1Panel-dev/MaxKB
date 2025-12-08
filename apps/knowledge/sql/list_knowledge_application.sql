SELECT
	*
FROM
	application
WHERE
	user_id = %s
UNION
SELECT
	*
FROM
	application
WHERE
	"id"::text in (select target from workspace_user_resource_permission where auth_target_type = 'APPLICATION' and 'VIEW' = any (permission_list))