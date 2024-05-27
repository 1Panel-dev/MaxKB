SELECT
	(SELECT "name" FROM "document" WHERE "id"=document_id) as document_name,
	*
FROM
	"paragraph"
