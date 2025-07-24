SELECT
    paragraph_id,
	comprehensive_score,
	comprehensive_score as similarity
FROM
	(
	SELECT DISTINCT ON
		("paragraph_id") ( 1 - distince ),* ,(1 - distince) AS comprehensive_score
	FROM
		( SELECT *, ( embedding.embedding::vector(%s) <=>  %s ) AS distince FROM embedding ${embedding_query} ORDER BY distince) TEMP
	ORDER BY
		paragraph_id,
		distince
	) DISTINCT_TEMP
WHERE comprehensive_score>%s
ORDER BY comprehensive_score DESC
LIMIT %s