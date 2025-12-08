SELECT
    resource_or_folder.*,
    CASE
		WHEN
	      wurp."permission" is null then 'NOT_AUTH'
		ELSE wurp."permission"
	END
FROM (
    SELECT
        "id"::text,
        "name",
        'MODEL' AS "auth_target_type",
        'model' AS "resource_type",
        user_id,
        workspace_id,
        provider as icon,
        'default' as folder_id,
        create_time
    FROM
        model
        ${query_set}
    UNION
    SELECT
        "id"::text,
        "name",
        'MODEL' AS "auth_target_type",
        'folder' AS "resource_type",
        user_id,
        workspace_id,
        provider as icon,
        'default' as folder_id,
        create_time
    FROM model
    ${folder_query_set}
    AND 1=0
) resource_or_folder
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
ON wurp.target = resource_or_folder."id"
${resource_query_set}
ORDER BY resource_or_folder.create_time DESC