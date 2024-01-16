SELECT *,to_json(dataset_setting) as dataset_setting,to_json(model_setting) as model_setting FROM ( SELECT * FROM application  ${application_custom_sql} UNION
	SELECT
		*
	FROM
		application
	WHERE
		application."id" IN ( SELECT team_member_permission.target FROM team_member team_member LEFT JOIN team_member_permission team_member_permission ON team_member_permission.member_id = team_member."id" ${team_member_permission_custom_sql})
	) temp_application ${default_sql}