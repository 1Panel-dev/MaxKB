SELECT
	"document".* ,
	to_json("document"."meta") as meta,
	to_json("document"."status_meta") as status_meta,
	 (SELECT "count"("id") FROM "paragraph" WHERE document_id="document"."id") as "paragraph_count"
FROM
	"document" "document"
