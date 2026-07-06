WITH scheduler AS (SELECT SPLIT_PART(id, ':', 2) as trigger_id,
                          next_run_time
                   FROM django_apscheduler_djangojob
                   WHERE id LIKE 'trigger:%%'),
     scheduler_summary AS (SELECT trigger_id,
                                  (ARRAY_AGG(next_run_time ORDER BY next_run_time))[1] AS next_run_time
                           FROM scheduler
                           GROUP BY trigger_id),
     trigger_task_summary AS (SELECT tt.trigger_id,
                                     JSON_AGG(
                                             JSON_BUILD_OBJECT(
                                                     'type', tt.source_type,
                                                     'name', COALESCE(app.name, tool.name),
                                                     'icon', COALESCE(app.icon, tool.icon)
                                             )
                                     )                                        AS trigger_task,
                                     STRING_AGG(COALESCE(app.name, tool.name), ' ') AS trigger_task_str
                              FROM event_trigger_task tt
                                       LEFT JOIN application app
                                                 ON tt.source_type = 'APPLICATION' AND tt.source_id = app.id
                                       LEFT JOIN tool ON tt.source_type = 'TOOL' AND tt.source_id = tool.id
                              GROUP BY tt.trigger_id)
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
            ss.next_run_time,
            COALESCE(tts.trigger_task, '[]'::JSON)         AS trigger_task,
            tts.trigger_task_str
      FROM event_trigger t
               LEFT JOIN scheduler_summary ss ON ss.trigger_id = t.id::text
               LEFT JOIN trigger_task_summary tts ON t.id = tts.trigger_id
          ${trigger_query_set}
      ) AS sub
    ${task_query_set}
ORDER BY sub.create_time DESC