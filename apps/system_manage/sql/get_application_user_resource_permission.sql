SELECT resource_or_folder.*,
       CASE
           WHEN wurp.permission IS NULL THEN 'NOT_AUTH'
           ELSE wurp.permission
       END
FROM (
         SELECT id::text,
                "name",
                'APPLICATION' AS "auth_target_type",
                'application' AS "resource_type",
                user_id,
                workspace_id,
                icon,
                folder_id,
                create_time
         FROM application
         ${query_set}
         UNION
         SELECT application_folder."id"::text,
                application_folder."name",
                'APPLICATION'                  AS "auth_target_type",
                'folder'                       AS "resource_type",
                application_folder."user_id",
                application_folder."workspace_id",
                NULL                           AS "icon",
                application_folder."parent_id" AS "folder_id",
                application_folder."create_time"
         FROM application_folder
         ${folder_query_set}
     ) resource_or_folder
LEFT JOIN (
    SELECT target,
           CASE
               WHEN auth_type = 'ROLE'
                   AND 'ROLE' = ANY (permission_list) THEN 'ROLE'
               WHEN auth_type = 'RESOURCE_PERMISSION_GROUP'
                   AND 'MANAGE' = ANY (permission_list) THEN 'MANAGE'
               WHEN auth_type = 'RESOURCE_PERMISSION_GROUP'
                   AND 'VIEW' = ANY (permission_list) THEN 'VIEW'
               ELSE NULL
               END AS permission
    FROM workspace_user_resource_permission
    ${workspace_user_resource_permission_query_set}
) wurp
ON wurp.target::text = resource_or_folder.id
${resource_query_set}
ORDER BY resource_or_folder.create_time DESC
