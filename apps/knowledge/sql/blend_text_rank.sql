SELECT
	id,
	paragraph_id,
	ts_rank_cd(search_vector, websearch_to_tsquery('simple', %s), 32) AS text_rank
FROM embedding ${embedding_query}
