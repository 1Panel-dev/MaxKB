UPDATE "document" "document"
SET status_meta = jsonb_set ( "document".status_meta, '{aggs}', tmp.status_meta )
FROM
	(
	SELECT COALESCE
		( jsonb_agg ( jsonb_delete ( ( row_to_json ( record ) :: JSONB ), 'document_id' ) ), '[]' :: JSONB ) AS status_meta,
		document_id AS document_id
	FROM
		(
		SELECT
			"paragraph".status,
			"count" ( "paragraph"."id" ),
			"document"."id" AS document_id
		FROM
			"document" "document"
			LEFT JOIN "paragraph" "paragraph" ON "document"."id" = paragraph.document_id
		${document_custom_sql}
		GROUP BY
			"paragraph".status,
			"document"."id"
		) record
	GROUP BY
		document_id
	) tmp
WHERE "document".id="tmp".document_id