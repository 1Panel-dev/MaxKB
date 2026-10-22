SELECT problem.*,
       (SELECT COUNT(ppm.id)
        FROM problem_paragraph_mapping ppm
                 INNER JOIN paragraph p ON ppm.paragraph_id = p.id
        WHERE ppm.problem_id = problem.id AND p.local_state <> 'deleted') AS "paragraph_count"
FROM problem problem
