SELECT
	problem."id" AS "source_id",
	problem.document_id AS document_id,
	problem.paragraph_id AS paragraph_id,
	problem.dataset_id AS dataset_id,
	0 AS source_type,
	problem."content" AS "text",
	paragraph.is_active AS is_active
FROM
	problem problem
	LEFT JOIN paragraph paragraph ON paragraph."id" = problem.paragraph_id
 ${problem}

UNION
SELECT
	paragraph."id" AS "source_id",
	paragraph.document_id AS document_id,
	paragraph."id" AS paragraph_id,
	paragraph.dataset_id AS dataset_id,
	1 AS source_type,
	paragraph."content" AS "text",
	paragraph.is_active AS is_active
FROM
	paragraph paragraph

 ${paragraph}