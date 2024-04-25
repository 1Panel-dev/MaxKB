SELECT
	paragraph.*,
	dataset."name" AS "dataset_name",
	"document"."name" AS "document_name",
	"document"."hit_handling_method" AS "hit_handling_method"
FROM
	paragraph paragraph
	LEFT JOIN dataset dataset ON dataset."id" = paragraph.dataset_id
	LEFT JOIN "document" "document" ON "document"."id" =paragraph.document_id