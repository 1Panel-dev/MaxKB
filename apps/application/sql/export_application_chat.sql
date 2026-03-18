SELECT application_chat_record_temp.id                     AS id,
       application_chat."id"                               as chat_id,
       application_chat.abstract                           as abstract,
       application_chat_record_temp.problem_text           as problem_text,
       application_chat_record_temp.answer_text            as answer_text,
       application_chat_record_temp.message_tokens         as message_tokens,
       application_chat_record_temp.answer_tokens          as answer_tokens,
       application_chat_record_temp.run_time               as run_time,
       application_chat_record_temp.details::JSON          as details, application_chat_record_temp."index" as "index",
       application_chat_record_temp.improve_paragraph_list as improve_paragraph_list,
       application_chat_record_temp.vote_status            as vote_status,
       application_chat_record_temp.create_time            as create_time,
       to_json(application_chat.asker)                     as asker
FROM application_chat application_chat

         LEFT JOIN (SELECT COUNT(acr."id")                                                  AS chat_record_count,
                           SUM((acr."vote_status" = '0')::int)                              AS star_num,
                           SUM((acr."vote_status" = '1')::int)                              AS trample_num,
                           SUM(COALESCE(array_length(acr.improve_paragraph_id_list, 1), 0)) AS mark_sum,
                           acr.chat_id
                    FROM application_chat_record acr
                    WHERE EXISTS (SELECT 1
                                  FROM application_chat ac2
                        ${inner_queryset}
                            AND ac2.id = acr.chat_id)
                    GROUP BY acr.chat_id) chat_record_temp
                   ON application_chat."id" = chat_record_temp.chat_id

         LEFT JOIN (SELECT acr.*,
                           COALESCE(p.paragraph_list, '{}') as improve_paragraph_list
                    FROM application_chat_record acr
                             LEFT JOIN LATERAL (
                        SELECT ARRAY_AGG(row_to_json(paragraph)) as paragraph_list
                        FROM paragraph
                        WHERE paragraph."id" = ANY (acr.improve_paragraph_id_list)
                            ) p ON TRUE) application_chat_record_temp
                   ON application_chat_record_temp.chat_id = application_chat."id"
    ${default_queryset}