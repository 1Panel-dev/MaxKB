from unittest import mock

from django.test import SimpleTestCase

from application.models import ChatRecord


class ChatRecordTestCase(SimpleTestCase):
    def test_save_removes_nul_characters(self):
        chat_record = ChatRecord(problem_text="question\x00text", answer_text="answer\x00text")

        with mock.patch("django.db.models.Model.save") as model_save:
            chat_record.save()

        self.assertEqual(chat_record.problem_text, "questiontext")
        self.assertEqual(chat_record.answer_text, "answertext")
        model_save.assert_called_once_with()
