SELECT
	"document".* ,
	to_json("document"."meta") as meta,
	 (SELECT "count"("id") FROM "paragraph" WHERE document_id="document"."id") as "paragraph_count"
FROM
	"document" "document"
