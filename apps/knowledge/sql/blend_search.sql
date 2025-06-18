SELECT
	paragraph_id,
	comprehensive_score,
	comprehensive_score AS similarity
FROM
	(
	SELECT DISTINCT ON
		( "paragraph_id" ) ( similarity ),* ,
		similarity AS comprehensive_score
	FROM
		(
		SELECT
			*,
			(( 1 - ( embedding.embedding <=>  %s ) )+ts_rank_cd( embedding.search_vector, websearch_to_tsquery('simple', %s ), 32 )) AS similarity
		FROM
			embedding ${embedding_query}
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