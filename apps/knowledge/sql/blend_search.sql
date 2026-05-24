WITH vector_top AS (
	SELECT id,
	       paragraph_id,
	       (embedding::vector(%s) <=> %s) AS distance
	FROM embedding ${embedding_query}
	ORDER BY (embedding::vector(%s) <=> %s)
	LIMIT LEAST(%s * 10, 500)
)
SELECT
	paragraph_id,
	comprehensive_score,
	comprehensive_score AS similarity
FROM
	(
	SELECT DISTINCT ON
		(vc.paragraph_id) vc.paragraph_id,
		(1 - vc.distance + COALESCE(ts_rank_cd(e.search_vector, websearch_to_tsquery('simple', %s), 32), 0)) AS comprehensive_score
	FROM
		vector_top vc
	JOIN embedding e ON e.id = vc.id
	ORDER BY
		vc.paragraph_id,
		comprehensive_score DESC
	) sub
WHERE comprehensive_score>%s
ORDER BY comprehensive_score DESC
LIMIT %s
