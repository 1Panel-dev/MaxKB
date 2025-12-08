SELECT resource_or_folder.*,
    CASE
        WHEN wurp.permission IS NULL THEN 'NOT_AUTH'
        ELSE wurp.permission
    END
FROM (
        SELECT
            id::text,
            "name",
            'KNOWLEDGE' AS "auth_target_type",
            'knowledge' AS "resource_type",
            user_id,
            workspace_id,
            "type"::varchar AS "icon",
            folder_id,
            create_time
        FROM knowledge
            ${query_set}
        UNION
        SELECT knowledge_folder."id"::text,
               knowledge_folder."name",
               'KNOWLEDGE'                  AS "auth_target_type",
                    'folder'                       AS "resource_type",
                    knowledge_folder."user_id",
                    knowledge_folder."workspace_id",
                    NULL                           AS "icon",
                    knowledge_folder."parent_id" AS "folder_id",
                    knowledge_folder."create_time"
        FROM knowledge_folder
        ${folder_query_set}
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
ON wurp.target::text = resource_or_folder.id
${resource_query_set}
ORDER BY resource_or_folder.create_time DESC