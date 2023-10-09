SELECT
	app_or_dataset.*,
	team_member_permission.member_id,
	team_member_permission.operate
FROM
	(
	SELECT
		"id",
		"name",
		'DATASET' AS "type",
		user_id
	FROM
		dataset
	WHERE
		"user_id" = %s UNION
	SELECT
		"id",
		"name",
		'APPLICATION' AS "type",
		user_id
	FROM
		application
	WHERE
		"user_id" = %s
	) app_or_dataset
	LEFT JOIN ( SELECT * FROM team_member_permission WHERE member_id = %s ) team_member_permission ON team_member_permission.target = app_or_dataset."id"