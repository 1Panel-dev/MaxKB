SELECT
	paragraph.*,
	knowledge."name" AS "knowledge_name",
	knowledge."type" AS "knowledge_type",
	"document"."name" AS "document_name",
	"document"."meta"::json AS "meta",
	"document"."hit_handling_method" AS "hit_handling_method",
	"document"."directly_return_similarity" as "directly_return_similarity"
FROM
	paragraph paragraph
	LEFT JOIN knowledge knowledge ON knowledge."id" = paragraph.knowledge_id
	LEFT JOIN "document" "document" ON "document"."id" =paragraph.document_id