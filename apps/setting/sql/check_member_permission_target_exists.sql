SELECT
	static_temp."target_id"::text
FROM
	(SELECT * FROM json_to_recordset(
   %s
  ) AS x(target_id uuid,type text)) static_temp
	LEFT JOIN (
	SELECT
		"id",
		'DATASET' AS "type",
		user_id,
		ARRAY [ 'MANAGE',
		'USE',
		'DELETE' ] AS "operate"
	FROM
		dataset
	WHERE
		"user_id" = %s UNION
	SELECT
		"id",
		'APPLICATION' AS "type",
		user_id,
		ARRAY [ 'MANAGE',
		'USE',
		'DELETE' ] AS "operate"
	FROM
		application
	WHERE
	"user_id" = %s
	) "app_and_dataset_temp"
	ON "app_and_dataset_temp"."id" = static_temp."target_id" and app_and_dataset_temp."type"=static_temp."type"
	WHERE app_and_dataset_temp.id is NULL ;