UPDATE "document"
SET "char_length" = ( SELECT "sum" ( "char_length" ( "content" ) ) FROM paragraph WHERE "document_id" = %s )
WHERE
	"id" = %s