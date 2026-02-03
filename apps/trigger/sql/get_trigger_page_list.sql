WITH scheduler AS (SELECT SPLIT_PART(id, ':', 2) as trigger_id,
                          id,
                          next_run_time
                   FROM django_apscheduler_djangojob
                   WHERE id LIKE 'trigger:%%')
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
             (SELECT nick_name FROM "user" WHERE id = t.user_id) AS create_user,
             COALESCE(
                     (ARRAY_AGG(sj.next_run_time ORDER BY sj.next_run_time))[1],
                     NULL
             )  as next_run_time,
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
               LEFT JOIN scheduler sj ON sj.trigger_id=t.id::text
               LEFT JOIN event_trigger_task tt ON t.id = tt.trigger_id
               LEFT JOIN application app ON tt.source_type = 'APPLICATION' AND tt.source_id = app.id
               LEFT JOIN tool ON tt.source_type = 'TOOL' AND tt.source_id = tool.id
          ${trigger_query_set}
      GROUP BY t.id, t.workspace_id, t.name, t.desc, t.trigger_type, t.trigger_setting, t.meta, t.is_active,
               t.create_time,
               t.update_time, t.user_id) AS sub
    ${task_query_set}
ORDER BY sub.create_time DESC