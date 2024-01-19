SELECT
	paragraph.*,
	dataset."name" AS "dataset_name",
	"document"."name" AS "document_name"
FROM
	paragraph paragraph
	LEFT JOIN dataset dataset ON dataset."id" = paragraph.dataset_id
	LEFT JOIN "document" "document" ON "document"."id" =paragraph.document_id