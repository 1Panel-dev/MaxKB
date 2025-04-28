SELECT
		problem.*,
		(SELECT "count"("id") FROM "problem_paragraph_mapping" WHERE problem_id="problem"."id") as "paragraph_count"
	FROM
		problem problem
