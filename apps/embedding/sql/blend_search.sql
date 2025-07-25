SELECT
	paragraph_id,
	comprehensive_score,
	comprehensive_score AS similarity
FROM
	(
	SELECT DISTINCT ON
		( "paragraph_id" ) ( 1 - distince + ts_similarity ) as similarity, *,
		(1 - distince + ts_similarity) AS comprehensive_score
	FROM
		(
		SELECT
			*,
			(embedding.embedding::vector(%s) <=>  %s) as distince,
			(ts_rank_cd( embedding.search_vector, websearch_to_tsquery('simple', %s ), 32 )) AS ts_similarity
		FROM
			embedding ${embedding_query}
		    ORDER BY distince
		) TEMP
	ORDER BY
		paragraph_id,
		similarity DESC
	) DISTINCT_TEMP
WHERE
	comprehensive_score >%s
ORDER BY
	comprehensive_score DESC
	LIMIT %s