import uuid

from django.test import TestCase
from django.utils import timezone

from application.models import Application, ApplicationChatUserStats, ApplicationFolder, Chat, ChatRecord
from common.auth.constants.role_constants import RoleConstants
from common.auth.struct.auth import Auth
from common.constants.resource_permission_constants import (
    AuthTargetType,
    ResourceAuthType,
    ResourcePermissionConstants,
)
from homepage.serializers.homepage import HomePageSerializer
from system_manage.models import WorkspaceUserResourcePermission
from users.models import User


class ApplicationMonitoringTests(TestCase):
    def setUp(self):
        self.workspace_id = "homepage-monitoring"
        self.today = timezone.localdate().strftime("%Y-%m-%d")
        self.user = User.objects.create(
            username="homepage-monitoring-user",
            nick_name="Homepage Monitoring User",
            password="x",
            role="USER",
        )
        folder = ApplicationFolder.objects.create(
            id="homepage-monitoring-folder",
            name="Homepage Monitoring",
            workspace_id=self.workspace_id,
            user=self.user,
        )
        self.authorized_application = Application.objects.create(
            name="Authorized Application",
            workspace_id=self.workspace_id,
            folder=folder,
            user=self.user,
        )
        self.unauthorized_application = Application.objects.create(
            name="Unauthorized Application",
            workspace_id=self.workspace_id,
            folder=folder,
            user=self.user,
        )
        WorkspaceUserResourcePermission.objects.create(
            workspace_id=self.workspace_id,
            user=self.user,
            auth_target_type=AuthTargetType.APPLICATION,
            target=str(self.authorized_application.id),
            auth_type=ResourceAuthType.RESOURCE_PERMISSION_GROUP,
            permission_list=[ResourcePermissionConstants.VIEW],
        )
        role = RoleConstants.USER.get_workspace_role()(None, {"workspace_id": self.workspace_id})
        self.auth = Auth(roles={str(role)}, permissions={})
        self._add_usage(self.authorized_application, "authorized-user", "0")
        self._add_usage(self.unauthorized_application, "unauthorized-user", "1")

    def _add_usage(self, application, chat_user_id, vote_status):
        chat = Chat.objects.create(
            application=application,
            abstract="",
            chat_user_id=chat_user_id,
            asker={"username": chat_user_id},
        )
        record = ChatRecord.objects.create(
            chat=chat,
            vote_status=vote_status,
            problem_text="question",
            answer_text="answer",
            message_tokens=1,
            answer_tokens=2,
            index=1,
        )
        stats = ApplicationChatUserStats.objects.create(
            application=application,
            chat_user_id=uuid.uuid4(),
            intraday_access_num=1,
        )
        now = timezone.now()
        ChatRecord.objects.filter(id=record.id).update(create_time=now)
        ApplicationChatUserStats.objects.filter(id=stats.id).update(create_time=now)

    def _get_trend(self, application_id):
        return HomePageSerializer.ApplicationMonitoring(
            data={
                "application_id": str(application_id),
                "user_id": self.user.id,
                "workspace_id": self.workspace_id,
                "start_time": self.today,
                "end_time": self.today,
            }
        ).get_chat_record_aggregate_trend(self.auth)

    def test_unauthorized_application_id_returns_empty_trend(self):
        trend = self._get_trend(self.unauthorized_application.id)

        self.assertEqual(
            trend,
            [
                {
                    "star_num": 0,
                    "trample_num": 0,
                    "tokens_num": 0,
                    "chat_record_count": 0,
                    "customer_num": 0,
                    "day": self.today,
                    "customer_added_count": 0,
                }
            ],
        )

    def test_authorized_application_id_returns_real_trend(self):
        trend = self._get_trend(self.authorized_application.id)

        self.assertEqual(trend[0]["star_num"], 1)
        self.assertEqual(trend[0]["tokens_num"], 3)
        self.assertEqual(trend[0]["chat_record_count"], 1)
        self.assertEqual(trend[0]["customer_num"], 1)
        self.assertEqual(trend[0]["customer_added_count"], 1)
