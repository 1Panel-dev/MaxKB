UPDATE "document"
SET "char_length" = ( SELECT CASE WHEN
		"sum" ( "char_length" ( "content" ) ) IS NULL THEN
			0 ELSE "sum" ( "char_length" ( "content" ) )
		END FROM paragraph WHERE "document_id" = %s )
WHERE
	"id" = %s