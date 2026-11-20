from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase

from application.models import Application, ApplicationFolder, Chat, ChatRecord, ChatShareLink
from application.serializers.application_chat_link import (
    ChatRecordShareLinkSerializer,
    ChatShareLinkDetailSerializer,
    save_public_file_access,
)
from common.exception.app_exception import AppApiException
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.utils.chat_link_code import UUIDEncoder
from knowledge.models import PublicFileAccess
from xpack.models.application_setting import ApplicationSetting


class ChatShareLinkFileAccessTests(TestCase):
    def test_registers_files_from_question_attachments_and_messages(self):
        answer_audio_id = "01a1f273-7bd3-7329-a5d6-cf476ef7a597"
        answer_image_id = "01a1f273-a20c-770f-8e9a-7cb0dfb5d0dc"
        record = SimpleNamespace(
            question={
                "type": "QUESTION",
                "content": "",
                "audio_list": [
                    {
                        "url": "./oss/file/01a1f272-85ca-7187-96f2-dbcdffa10f2e",
                        "name": "audio.mp3",
                    }
                ],
                "image_list": [
                    {
                        "url": "./oss/file/01a1f272-868f-7588-93e5-2fbaef22b6b1",
                        "name": "image.jpg",
                    }
                ],
            },
            messages=[
                {"type": "TEXT", "content": f'<audio src="./oss/file/{answer_audio_id}" controls></audio>'},
                {"type": "TEXT", "content": f"![Image](./oss/file/{answer_image_id})"},
            ],
            answer_text_list=[[]],
        )

        save_public_file_access([record])

        self.assertSetEqual(
            set(PublicFileAccess.objects.filter(source_type="FILE").values_list("source_id", flat=True)),
            {
                "01a1f272-85ca-7187-96f2-dbcdffa10f2e",
                "01a1f272-868f-7588-93e5-2fbaef22b6b1",
                answer_audio_id,
                answer_image_id,
            },
        )

    def test_opening_existing_share_link_registers_record_files(self):
        DatabaseModelManage.init()
        folder, _ = ApplicationFolder.objects.get_or_create(id="default", defaults={"name": "默认分组"})
        application = Application.objects.create(name="测试应用", folder=folder)
        chat = Chat.objects.create(application=application, abstract="历史分享")
        question_image_id = "01a1f272-868f-7588-93e5-2fbaef22b6b1"
        answer_audio_id = "01a1f273-7bd3-7329-a5d6-cf476ef7a597"
        record = ChatRecord.objects.create(
            chat=chat,
            problem_text="",
            answer_text="",
            index=1,
            question={
                "type": "QUESTION",
                "content": "",
                "image_list": [{"url": f"./oss/file/{question_image_id}", "name": "image.jpg"}],
            },
            messages=[{"type": "TEXT", "content": f'<audio src="./oss/file/{answer_audio_id}" controls></audio>'}],
        )
        share_link = ChatShareLink.objects.create(
            chat=chat,
            application=application,
            chat_record_ids=[record.id],
        )

        ChatShareLinkDetailSerializer(data={"link": UUIDEncoder.encode(share_link.id)}).get_record_list()

        self.assertSetEqual(
            set(PublicFileAccess.objects.filter(source_type="FILE").values_list("source_id", flat=True)),
            {question_image_id, answer_audio_id},
        )


class ChatShareLinkAvatarTests(TestCase):
    def test_detail_returns_configured_avatars(self):
        DatabaseModelManage.init()
        folder, _ = ApplicationFolder.objects.get_or_create(id="default", defaults={"name": "默认分组"})
        application = Application.objects.create(name="测试应用", folder=folder)
        chat = Chat.objects.create(application=application, abstract="分享对话")
        share_link = ChatShareLink.objects.create(
            chat=chat,
            application=application,
            chat_record_ids=[],
        )
        ApplicationSetting.objects.create(
            application=application,
            avatar="./oss/file/assistant-avatar",
            show_avatar=True,
            user_avatar="./oss/file/user-avatar",
            show_user_avatar=True,
            custom_theme={"theme_color": "#123456", "header_font_color": "#ffffff"},
            chat_background="./oss/file/chat-background",
        )

        with patch("django.core.cache.cache.get", return_value=True):
            detail = ChatShareLinkDetailSerializer(data={"link": UUIDEncoder.encode(share_link.id)}).get_record_list()

        self.assertEqual(
            detail["app_info"],
            {
                "avatar": "./oss/file/assistant-avatar",
                "show_avatar": True,
                "user_avatar": "./oss/file/user-avatar",
                "show_user_avatar": True,
                "custom_theme": {"theme_color": "#123456", "header_font_color": "#ffffff"},
                "chat_background": "./oss/file/chat-background",
            },
        )


class ChatShareLinkSettingTests(TestCase):
    def setUp(self):
        DatabaseModelManage.init()
        folder, _ = ApplicationFolder.objects.get_or_create(id="default", defaults={"name": "默认分组"})
        self.application = Application.objects.create(name="测试应用", folder=folder)
        self.user_id = "01a1f6cf-9369-77d2-abf6-70f9db09c494"
        self.chat = Chat.objects.create(
            application=self.application,
            abstract="分享对话",
            chat_user_id=self.user_id,
        )

    def test_generate_link_rejects_disabled_share_setting_with_valid_license(self):
        ApplicationSetting.objects.create(application=self.application, show_share=False)

        with patch("django.core.cache.cache.get", return_value=True):
            with self.assertRaises(AppApiException):
                ChatRecordShareLinkSerializer(
                    data={
                        "application_id": self.application.id,
                        "chat_id": self.chat.id,
                        "user_id": self.user_id,
                    }
                ).generate_link({"is_current_all": True})

        self.assertFalse(ChatShareLink.objects.filter(chat=self.chat).exists())

    def test_generate_link_keeps_sharing_when_license_is_invalid(self):
        ApplicationSetting.objects.create(application=self.application, show_share=False)

        with patch("django.core.cache.cache.get", return_value=False):
            result = ChatRecordShareLinkSerializer(
                data={
                    "application_id": self.application.id,
                    "chat_id": self.chat.id,
                    "user_id": self.user_id,
                }
            ).generate_link({"is_current_all": True})

        self.assertTrue(result["link"])
        self.assertTrue(ChatShareLink.objects.filter(chat=self.chat).exists())

    def test_community_without_application_setting_model_keeps_sharing_available(self):
        with patch.dict(DatabaseModelManage.model_dict, {"application_setting": None}):
            result = ChatRecordShareLinkSerializer(
                data={
                    "application_id": self.application.id,
                    "chat_id": self.chat.id,
                    "user_id": self.user_id,
                }
            ).generate_link({"is_current_all": True})
            detail = ChatShareLinkDetailSerializer(data={"link": result["link"]}).get_record_list()

        self.assertEqual(detail["app_info"], {})

    def test_opening_share_link_rejects_disabled_share_setting_with_valid_license(self):
        ApplicationSetting.objects.create(application=self.application, show_share=False)
        share_link = ChatShareLink.objects.create(
            chat=self.chat,
            application=self.application,
            chat_record_ids=[],
        )

        with patch("django.core.cache.cache.get", return_value=True):
            with self.assertRaises(AppApiException):
                ChatShareLinkDetailSerializer(data={"link": UUIDEncoder.encode(share_link.id)}).get_record_list()
