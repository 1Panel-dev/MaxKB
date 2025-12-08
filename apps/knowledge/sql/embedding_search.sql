SELECT
    paragraph_id,
	comprehensive_score,
	comprehensive_score as similarity
FROM
	(
	SELECT DISTINCT ON
		("paragraph_id") ( 1 - distance ),* ,(1 - distance) AS comprehensive_score
	FROM
		( SELECT *, ( embedding.embedding::vector(%s) <=>  %s ) AS distance FROM embedding ${embedding_query} ORDER BY distance) TEMP
	ORDER BY
		paragraph_id,
		distance
	) DISTINCT_TEMP
WHERE comprehensive_score>%s
ORDER BY comprehensive_score DESC
LIMIT %s