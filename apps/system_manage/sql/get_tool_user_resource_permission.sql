SELECT resource_or_folder.*,
    CASE
		WHEN wurp."permission" IS NULL THEN 'NOT_AUTH'
		ELSE wurp."permission"
	END
FROM (
        SELECT "id"::text,
                "name",
                'TOOL' AS "auth_target_type",
                'tool' AS "resource_type",
                user_id,
                workspace_id,
                icon,
                folder_id,
                tool_type,
                create_time
        FROM tool
        ${query_set}
        UNION
        SELECT tool_folder."id"::text,
               tool_folder."name",
               'TOOL'                  AS "auth_target_type",
               'folder'                AS "resource_type",
               tool_folder."user_id",
               tool_folder."workspace_id",
               NULL                    AS "icon",
               tool_folder."parent_id" AS "folder_id",
               NULL                    AS "tool_type",
               tool_folder."create_time"
        FROM tool_folder
        ${folder_query_set}
    ) resource_or_folder
LEFT JOIN (
    SELECT target,
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
ON wurp.target::text = resource_or_folder."id"
${resource_query_set}
ORDER BY resource_or_folder.create_time DESC

