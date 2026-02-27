SELECT * from (
SELECT
    "document".*,
    to_json("document"."meta") as meta,
    to_json("document"."status_meta") as status_meta,
    (SELECT "count"("id") FROM "paragraph" WHERE document_id = "document"."id") as "paragraph_count",
    tag_agg.tag_count as "tag_count",
    COALESCE(tag_agg.tags, '[]'::json) as "tags"
FROM
    "document" "document"
LEFT JOIN LATERAL (
    SELECT
        COUNT(*)::int as tag_count,
        json_agg(
            json_build_object(
                'id', "tag"."id",
                'key', "tag"."key",
                'value', "tag"."value"
            )
            ORDER BY "tag"."key", "tag"."value"
        ) as tags
    FROM "document_tag" "document_tag"
    INNER JOIN "tag" "tag" ON "tag"."id" = "document_tag"."tag_id"
    WHERE "document_tag"."document_id" = "document"."id"
) tag_agg ON TRUE
${document_custom_sql}
) temp
${order_by_query}