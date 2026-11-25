from unittest.mock import patch
from django.test import TestCase
from application.models import Application, ApplicationFolder, Chat, ChatRecord
from application.serializers.application_chat_record import ApplicationChatRecordImproveSerializer
from knowledge.models import Document, Knowledge, Paragraph


class AnnotationWriteTests(TestCase):
    def test_authorized_annotation_updates_the_selected_chat(self):
        folder, _ = ApplicationFolder.objects.get_or_create(id="default", defaults={"name": "default"})
        app = Application.objects.create(name="annotation", folder=folder)
        chat = Chat.objects.create(application=app, abstract="question")
        record = ChatRecord.objects.create(chat=chat, problem_text="question", answer_text="answer", index=1)
        knowledge = Knowledge.objects.create(name="annotation", desc="", workspace_id="default")
        document = Document.objects.create(knowledge=knowledge, name="annotations", char_length=0)
        serializer = ApplicationChatRecordImproveSerializer(
            data={
                "chat_id": chat.id,
                "chat_record_id": record.id,
                "application_id": app.id,
                "workspace_id": "default",
                "knowledge_id": knowledge.id,
                "document_id": document.id,
            }
        )
        module = "application.serializers.application_chat_record."
        with (
            patch(module + "get_is_permissions", return_value=lambda *args: True),
            patch(module + "get_embedding_model_id_by_knowledge_id"),
            patch(module + "embedding_by_paragraph"),
            patch(module + "ChatCountSerializer") as counts,
        ):
            serializer.improve({"content": "reviewed answer"})
        counts.assert_called_once_with(data={"chat_id": chat.id})
        record.refresh_from_db()
        self.assertTrue(Paragraph.objects.filter(id__in=record.improve_paragraph_id_list, document=document).exists())
