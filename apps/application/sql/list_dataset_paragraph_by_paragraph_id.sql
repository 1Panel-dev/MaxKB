SELECT
	paragraph.*,
	dataset."name" AS "dataset_name"
FROM
	paragraph paragraph
	LEFT JOIN dataset dataset ON dataset."id" = paragraph.dataset_id