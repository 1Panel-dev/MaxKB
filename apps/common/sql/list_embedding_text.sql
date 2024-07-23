SELECT
	problem_paragraph_mapping."id" AS "source_id",
	paragraph.document_id AS document_id,
	paragraph."id" AS paragraph_id,
	problem.dataset_id AS dataset_id,
	0 AS source_type,
	problem."content" AS "text",
	paragraph.is_active AS is_active
FROM
	problem problem
	LEFT JOIN problem_paragraph_mapping problem_paragraph_mapping ON problem_paragraph_mapping.problem_id=problem."id"
	LEFT JOIN paragraph paragraph ON paragraph."id" = problem_paragraph_mapping.paragraph_id
 ${problem}

UNION
SELECT
	paragraph."id" AS "source_id",
	paragraph.document_id AS document_id,
	paragraph."id" AS paragraph_id,
	paragraph.dataset_id AS dataset_id,
	1 AS source_type,
	concat_ws(E'\n',paragraph.title,paragraph."content") AS "text",
	paragraph.is_active AS is_active
FROM
	paragraph paragraph

 ${paragraph}