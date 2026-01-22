
SELECT *
FROM (SELECT t.id,
             t.workspace_id,
             t.name,
             t."desc",
             t.trigger_type,
             t.trigger_setting,
             t.meta::JSON,
             t.is_active,
             t.create_time,
             t.update_time,
             t.user_id,
             COALESCE(
                     JSON_AGG(
                             JSON_BUILD_OBJECT(
                                     'type', tt.source_type,
                                     'name', COALESCE(app.name, tool.name),
                                     'icon', COALESCE(app.icon, tool.icon)
                             )
                     ), '[]'::JSON
             )                                              AS trigger_task,
             STRING_AGG(COALESCE(app.name, tool.name), ' ') AS trigger_task_str
      FROM event_trigger t
               LEFT JOIN event_trigger_task tt ON t.id = tt.trigger_id
               LEFT JOIN application app ON tt.source_type = 'APPLICATION' AND tt.source_id = app.id
               LEFT JOIN tool ON tt.source_type = 'TOOL' AND tt.source_id = tool.id
          ${trigger_query_set}
      GROUP BY t.id, t.workspace_id, t.name, t.desc, t.trigger_type, t.trigger_setting, t.meta, t.is_active,
               t.create_time,
               t.update_time, t.user_id) AS sub
    ${task_query_set}
ORDER BY sub.create_time DESC