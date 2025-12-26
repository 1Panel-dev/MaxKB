WITH source_data_cte AS (
    SELECT 'APPLICATION' as source_type, id, "name", "desc","user_id"
    FROM application
    UNION ALL
    SELECT 'KNOWLEDGE' as source_type, id, "name", "desc","user_id"
    FROM knowledge)
SELECT rm.*,
       sdc.*
FROM resource_mapping rm
         LEFT JOIN source_data_cte sdc
                   ON rm.source_type = sdc.source_type
                       AND rm.source_id::uuid = sdc.id