SELECT
	"document".* ,
	 (SELECT "count"("id") FROM "paragraph" WHERE document_id="document"."id") as "paragraph_count"
FROM
	"document" "document"
