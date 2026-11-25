from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from application.models import ChatUserType
from application.workflow.common import Node
from application.workflow.nodes.ai_chat_node.tools.application import get_application_func
from application.workflow.nodes.application_node.application_node import ApplicationNode
from common.auth.struct.auth import Auth
from common.exception.app_exception import AppApiException


class _ReachedChildExecution(Exception):
    pass


class ApplicationWorkflowChildAuthorizationTests(SimpleTestCase):
    chat_user_id = "01a1f6cf-9369-77d2-abf6-70f9db09c494"
    parent_application_id = "00000000-0000-0000-0000-000000000001"
    child_application_id = "00000000-0000-0000-0000-000000000002"

    def workflow_params(self):
        return {
            "application_id": self.parent_application_id,
            "chat_id": "00000000-0000-0000-0000-000000000003",
            "chat_user_id": self.chat_user_id,
            "chat_user_type": ChatUserType.CHAT_USER.value,
            "debug": False,
            "ip_address": "127.0.0.1",
        }

    def application_node(self):
        node = Node(
            "application-node",
            "application-node",
            0,
            0,
            {
                "stepName": "child application",
                "node_data": {
                    "application_id": self.child_application_id,
                    "question_reference_address": [],
                },
            },
        )
        workflow_manage = MagicMock()
        workflow_manage.get_parameters.return_value = self.workflow_params()
        workflow_manage.get_context.return_value = None
        return ApplicationNode(node, workflow_manage, lambda item: item.properties["node_data"])

    @contextmanager
    def child_authorization(
        self,
        *,
        authorized,
        allowed_login_type="LOCAL",
        source="LOCAL",
        permission_application_id=None,
    ):
        permission_application_id = permission_application_id or self.child_application_id

        def get_child_auth(login_type, user_id, application_id):
            permissions = {}
            if authorized and login_type == allowed_login_type:
                permissions[f"CHAT_USER:r:{permission_application_id}"] = 1 << 1
            return Auth(set(), permissions)

        with (
            patch("application.models.application_access_token.ApplicationAccessToken.objects.filter") as access_token,
            patch("system_manage.models.chat_user.ChatUser.objects.filter") as chat_user_filter,
            patch("application.serializers.application.validate_application_bindings"),
            patch(
                "system_manage.services.chat_user_authorization.get_auth",
                side_effect=get_child_auth,
            ),
        ):
            access_token.return_value.exists.return_value = True
            chat_user_filter.return_value.only.return_value.first.return_value = SimpleNamespace(source=source)
            yield

    def test_application_node_rejects_unauthorized_chat_user_for_child_application(self):
        with (
            self.child_authorization(authorized=False),
            patch(
                "application.workflow.nodes.application_node.application_node.Chat.objects.get_or_create",
                side_effect=_ReachedChildExecution,
            ) as get_or_create,
            self.assertRaises(AppApiException) as raised,
        ):
            self.application_node().execute()

        self.assertEqual(raised.exception.code, 1005)
        get_or_create.assert_not_called()

    def test_agent_tool_rejects_unauthorized_chat_user_for_child_application(self):
        run_application = get_application_func(
            source_type="APPLICATION",
            source_id=self.parent_application_id,
            application=SimpleNamespace(id=self.child_application_id, name="child application"),
            workflow_params=self.workflow_params(),
            workspace_id="default",
            cancel_event=MagicMock(),
        )

        with (
            self.child_authorization(authorized=False),
            patch(
                "application.models.application_chat.Chat.objects.get_or_create",
                side_effect=_ReachedChildExecution,
            ) as get_or_create,
            self.assertRaises(AppApiException) as raised,
        ):
            run_application("weather")

        self.assertEqual(raised.exception.code, 1005)
        get_or_create.assert_not_called()

    def test_application_node_allows_authorized_chat_user_for_child_application(self):
        with (
            self.child_authorization(authorized=True, source="local"),
            patch(
                "application.workflow.nodes.application_node.application_node.Chat.objects.get_or_create",
                side_effect=_ReachedChildExecution,
            ),
            self.assertRaises(_ReachedChildExecution),
        ):
            self.application_node().execute()

    def test_application_node_rejects_child_application_when_login_source_is_not_allowed(self):
        with (
            self.child_authorization(authorized=True, allowed_login_type="OIDC", source="LOCAL"),
            patch(
                "application.workflow.nodes.application_node.application_node.Chat.objects.get_or_create",
                side_effect=_ReachedChildExecution,
            ) as get_or_create,
            self.assertRaises(AppApiException) as raised,
        ):
            self.application_node().execute()

        self.assertEqual(raised.exception.code, 1005)
        get_or_create.assert_not_called()

    def test_parent_application_permission_does_not_authorize_child_application(self):
        with (
            self.child_authorization(
                authorized=True,
                permission_application_id=self.parent_application_id,
            ),
            patch(
                "application.workflow.nodes.application_node.application_node.Chat.objects.get_or_create",
                side_effect=_ReachedChildExecution,
            ) as get_or_create,
            self.assertRaises(AppApiException) as raised,
        ):
            self.application_node().execute()

        self.assertEqual(raised.exception.code, 1005)
        get_or_create.assert_not_called()
