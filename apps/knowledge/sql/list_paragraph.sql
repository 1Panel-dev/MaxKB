SELECT
    (SELECT "name" FROM "document" WHERE "id"=document_id) as document_name,
	(SELECT "name" FROM "knowledge" WHERE "id"=knowledge_id) as knowledge_name,
	*
FROM
	"paragraph"
