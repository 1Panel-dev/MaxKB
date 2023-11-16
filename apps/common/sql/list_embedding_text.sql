SELECT
	problem."id" AS "source_id",
	problem.document_id AS document_id,
	problem.paragraph_id AS paragraph_id,
	problem.dataset_id AS dataset_id,
	0 AS source_type,
	problem."content" AS "text",
	paragraph.is_active AS is_active,
	problem.star_num as star_num,
	problem.trample_num as trample_num
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
	concat_ws(':',paragraph."title",paragraph."content") AS "text",
	paragraph.is_active AS is_active,
	paragraph.star_num as star_num,
	paragraph.trample_num as trample_num
FROM
	paragraph paragraph

 ${paragraph}