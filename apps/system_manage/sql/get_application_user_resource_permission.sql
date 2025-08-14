SELECT
    app_or_knowledge.*,
    CASE
		WHEN
	      wurp."permission" is null then 'NOT_AUTH'
		ELSE wurp."permission"
	END
FROM (
    SELECT
        "id",
        "name",
        'APPLICATION' AS "auth_target_type",
        user_id,
        workspace_id,
        icon,
        folder_id
    FROM
        application
        ${query_set}
) app_or_knowledge
LEFT JOIN (
    SELECT
        target,
        CASE
            WHEN auth_type = 'ROLE'
                AND 'ROLE' = ANY(permission_list) THEN 'ROLE'
            WHEN auth_type = 'RESOURCE_PERMISSION_GROUP'
                AND 'MANAGE' = ANY(permission_list) THEN 'MANAGE'
            WHEN auth_type = 'RESOURCE_PERMISSION_GROUP'
                AND 'VIEW' = ANY(permission_list) THEN 'VIEW'
            ELSE null
        END AS permission
    FROM
        workspace_user_resource_permission
        ${workspace_user_resource_permission_query_set}
) wurp
ON wurp.target = app_or_knowledge."id"
${resource_query_set}