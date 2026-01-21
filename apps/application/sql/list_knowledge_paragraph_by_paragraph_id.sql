SELECT DISTINCT ON (paragraph."id")
	paragraph.*,
	knowledge."name" AS "knowledge_name",
	knowledge."type" AS "knowledge_type",
	"document"."name" AS "document_name",
	"document"."meta"::json AS "meta",
	"document"."hit_handling_method" AS "hit_handling_method",
	"document"."directly_return_similarity" as "directly_return_similarity",
	-- PageIndex 章节路径信息
	page_index_node."id" AS "page_index_node_id",
	page_index_node."title" AS "section_title",
	page_index_node."level" AS "tree_level",
	page_index_node."path" AS "tree_path",
	page_index_node."order" AS "sibling_index"
FROM
	paragraph paragraph
	LEFT JOIN knowledge knowledge ON knowledge."id" = paragraph.knowledge_id
	LEFT JOIN "document" "document" ON "document"."id" = paragraph.document_id
	LEFT JOIN LATERAL (
		SELECT * FROM embedding
		WHERE embedding.paragraph_id = paragraph."id" AND embedding.source_type = 1
		LIMIT 1
	) embedding ON true
	LEFT JOIN page_index_node page_index_node ON page_index_node."id" = embedding.page_index_node_id