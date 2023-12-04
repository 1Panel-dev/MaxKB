SELECT
	*
FROM
	application
WHERE
	user_id = %s UNION
SELECT
	*
FROM
	application
WHERE
	"id" IN (
	SELECT
		team_member_permission.target
	FROM
		team_member team_member
		LEFT JOIN team_member_permission team_member_permission ON team_member_permission.member_id = team_member."id"
	WHERE
	( "team_member_permission"."auth_target_type" = 'APPLICATION' AND "team_member_permission"."operate"::text[] @> ARRAY['USE']  AND team_member.team_id = %s AND team_member.user_id =%s )
	)