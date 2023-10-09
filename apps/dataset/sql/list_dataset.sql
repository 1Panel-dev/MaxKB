SELECT
	dataset.*,
	document_temp."char_length",
	"document_temp".document_count
FROM
	dataset dataset
	LEFT JOIN ( SELECT "count" ( "id" ) AS document_count, "sum" ( "char_length" ) "char_length", dataset_id FROM "document" GROUP BY dataset_id ) "document_temp" ON dataset."id" = "document_temp".dataset_id