SELECT
	*
FROM
	(
	SELECT
		"temp_dataset".*,
		"document_temp"."char_length",
		"document_temp".document_count FROM (
			SELECT dataset.*
		FROM
			dataset dataset
		${dataset_custom_sql}
			 UNION
		SELECT
			*
		FROM
			dataset
		WHERE
			dataset."id" IN (
			SELECT
				team_member_permission.target
			FROM
				team_member team_member
				LEFT JOIN team_member_permission team_member_permission ON team_member_permission.member_id = team_member."id"
			${team_member_permission_custom_sql}
			)
		) temp_dataset
		LEFT JOIN ( SELECT "count" ( "id" ) AS document_count, "sum" ( "char_length" ) "char_length", dataset_id FROM "document" GROUP BY dataset_id ) "document_temp" ON temp_dataset."id" = "document_temp".dataset_id
	) temp
	${default_sql}