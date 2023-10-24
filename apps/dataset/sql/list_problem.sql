SELECT
		problem."id",
		problem."content",
		problem_paragraph_mapping.hit_num,
		problem_paragraph_mapping.star_num,
		problem_paragraph_mapping.trample_num,
		problem_paragraph_mapping.paragraph_id
	FROM
		problem problem
		LEFT JOIN problem_paragraph_mapping problem_paragraph_mapping ON problem."id" = problem_paragraph_mapping.problem_id
