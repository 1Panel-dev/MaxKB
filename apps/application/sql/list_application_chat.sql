select application_chat.*,application_chat.asker::json AS asker
from application_chat application_chat
${default_queryset}