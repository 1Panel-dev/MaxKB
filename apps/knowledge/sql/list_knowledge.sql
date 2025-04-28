SELECT
	*,
	to_json(meta) as meta
FROM
	(
	SELECT
		"temp_knowledge".*,
		"document_temp"."char_length",
		CASE
		WHEN
		"app_knowledge_temp"."count" IS NULL THEN 0 ELSE "app_knowledge_temp"."count" END AS application_mapping_count,
		"document_temp".document_count FROM (
			SELECT knowledge.*
		FROM
			knowledge knowledge
		${knowledge_custom_sql}
			 UNION
		SELECT
			*
		FROM
			knowledge
		WHERE
			knowledge."id" IN (
			SELECT
				team_member_permission.target
			FROM
				team_member team_member
				LEFT JOIN team_member_permission team_member_permission ON team_member_permission.member_id = team_member."id"
			${team_member_permission_custom_sql}
			)
		) temp_knowledge
		LEFT JOIN ( SELECT "count" ( "id" ) AS document_count, "sum" ( "char_length" ) "char_length", knowledge_id FROM "document" GROUP BY knowledge_id ) "document_temp" ON temp_knowledge."id" = "document_temp".knowledge_id
		LEFT JOIN (SELECT "count"("id"),knowledge_id FROM application_knowledge_mapping GROUP BY knowledge_id) app_knowledge_temp  ON temp_knowledge."id" = "app_knowledge_temp".knowledge_id
	) temp
	${default_sql}