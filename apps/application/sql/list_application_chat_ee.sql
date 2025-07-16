select application_chat.*,(CASE WHEN "chat_user".id is NULL THEN application_chat.asker ELSE jsonb_build_object('id',chat_user.id,'username',chat_user.username)  END)::json AS asker
from application_chat application_chat
         left join chat_user chat_user on chat_user.id::varchar = application_chat.chat_user_id
${default_queryset}