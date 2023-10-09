SELECT
	"id",
	'DATASET' AS "type",
	user_id,
	ARRAY [ 'MANAGE',
	'USE','DELETE' ] AS "operate"
FROM
	dataset
WHERE
	"user_id" = %s UNION
SELECT
	"id",
	'APPLICATION' AS "type",
	user_id,
	ARRAY [ 'MANAGE',
	'USE','DELETE' ] AS "operate"
FROM
	application
WHERE
	"user_id" = %s UNION
SELECT
	team_member_permission.target AS "id",
	team_member_permission.auth_target_type AS "type",
	team_member.user_id AS user_id,
	team_member_permission.operate AS "operate"
FROM
	team_member team_member
	LEFT JOIN team_member_permission team_member_permission ON team_member.ID = team_member_permission.member_id
WHERE
	team_member.user_id = %s AND team_member_permission.target IS NOT NULL