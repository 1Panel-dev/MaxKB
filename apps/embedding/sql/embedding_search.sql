SELECT * FROM (SELECT
	*,
	( 1 - ( embedding.embedding <=>  %s ) ) AS similarity,
CASE

		WHEN embedding.star_num - embedding.trample_num = 0 THEN
		0 ELSE ( ( ( embedding.star_num - embedding.trample_num ) - aggs.min_value ) / ( aggs.max_value - aggs.min_value ) )
	END AS score
FROM
	embedding,
	( SELECT MIN ( star_num - trample_num ) AS min_value, MAX ( star_num - trample_num ) AS max_value FROM embedding ${embedding_query}) aggs
	 ${embedding_query}
	) temp
	WHERE similarity>0.5
	ORDER BY (similarity + score) DESC LIMIT 1