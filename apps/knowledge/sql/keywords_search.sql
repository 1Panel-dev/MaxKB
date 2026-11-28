SELECT
    paragraph_id,
	comprehensive_score,
	comprehensive_score as similarity
FROM
	(
	SELECT DISTINCT ON
		("paragraph_id") ( similarity ),* ,similarity AS comprehensive_score
	FROM
		( SELECT *,ts_rank_cd(embedding.search_vector,websearch_to_tsquery('simple',%s),32) AS similarity  FROM embedding ${keywords_query}
		AND COALESCE(search_vector @@ websearch_to_tsquery('simple',%s), false)
		AND (SELECT count(*) FROM json_array_elements_text(%s::json) AS t(w) WHERE t.w = ANY(tsvector_to_array(embedding.search_vector))) >= %s) TEMP
	ORDER BY
		paragraph_id,
		similarity DESC
	) DISTINCT_TEMP
WHERE comprehensive_score>%s
ORDER BY comprehensive_score DESC
LIMIT %s
