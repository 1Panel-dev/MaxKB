SELECT
	static_temp."target_id"::text
FROM
	(SELECT * FROM json_to_recordset(
    %s
  ) AS x(target_id uuid,auth_target_type text)) static_temp
	LEFT JOIN (
	SELECT
		"id",
		'KNOWLEDGE' AS "auth_target_type"
	FROM
		knowledge
	WHERE workspace_id= %s
	UNION
	SELECT
		"id",
		'APPLICATION' AS "auth_target_type"
	FROM
		application
	WHERE workspace_id= %s
		UNION
	SELECT
		"id",
		'MODEL' AS "auth_target_type"
	FROM
		model
	WHERE workspace_id= %s
	UNION
	SELECT
		"id",
		'TOOL' AS "auth_target_type"
	FROM
		tool
	WHERE workspace_id= %s
	) "app_and_knowledge_temp"
	ON "app_and_knowledge_temp"."id" = static_temp."target_id" and app_and_knowledge_temp."auth_target_type"=static_temp."auth_target_type"
	WHERE app_and_knowledge_temp.id is NULL ;