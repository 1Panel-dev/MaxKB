SELECT
    DISTINCT u.id,
    u.nick_name,
    u.username,
    tmp.role_name_list AS role_name,
    CASE
        WHEN wurp."permission" IS NULL THEN 'NOT_AUTH'
        ELSE wurp."permission"
    END AS permission
FROM
    public."user" u
LEFT JOIN (
    SELECT
        user_id,
        CASE
            WHEN auth_type = 'ROLE'
                 AND 'ROLE' = ANY(permission_list) THEN 'ROLE'
            WHEN auth_type = 'RESOURCE_PERMISSION_GROUP'
                 AND 'MANAGE' = ANY(permission_list) THEN 'MANAGE'
            WHEN auth_type = 'RESOURCE_PERMISSION_GROUP'
                 AND 'VIEW' = ANY(permission_list) THEN 'VIEW'
            ELSE NULL
        END AS "permission"
    FROM
        workspace_user_resource_permission
    ${workspace_user_resource_permission_query_set}
) wurp ON u.id = wurp.user_id
LEFT JOIN (
    SELECT
        ARRAY_AGG(role_setting.role_name) AS role_name_list,
        ARRAY_AGG(role_setting.role_name)::text AS role_name_list_str,
        ARRAY_AGG(role_setting.type) AS type_list,
        user_role_relation.user_id
    FROM user_role_relation user_role_relation
    LEFT JOIN role_setting role_setting
    ON role_setting.id = user_role_relation.role_id
    ${role_name_and_type_query_set}
    GROUP BY
    user_role_relation.user_id) tmp
ON u.id = tmp.user_id
${user_query_set}