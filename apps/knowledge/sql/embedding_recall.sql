SELECT
	id,
	paragraph_id,
	source_id,
	source_type,
	meta,
	(1 - (embedding::vector(%s) <=> %s)) AS similarity
FROM embedding ${embedding_query}
AND embedding IS NOT NULL
ORDER BY (embedding::vector(%s) <=> %s)
LIMIT LEAST(%s * 10, 500)
