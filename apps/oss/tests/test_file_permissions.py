"""File reads retain workspace authorization outside system download endpoints."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from common.auth.constants.permission_constants import PermissionConstants
from common.exception.app_exception import AppUnauthorizedFailed
from knowledge.models import Document, File, FileSourceType, Knowledge
from oss.serializers.file import FileSerializer, _auth_system, _check_workspace_resource_permission
from system_manage.models import WorkspaceUserResourcePermission
from users.models import User


class FilePermissionTests(SimpleTestCase):
    def setUp(self):
        self.auth = SimpleNamespace(roles=set(), permissions={})
        self.grants = MagicMock()
        self.grants.filter.return_value = self.grants
        self.grants.exists.return_value = False
        self.user_query = MagicMock()
        self.user_query.filter.return_value.first.return_value = SimpleNamespace(id="user")
        self.document_query = MagicMock()
        self.document_query.filter.return_value.values_list.return_value.first.return_value = "knowledge"
        self.knowledge_query = MagicMock()
        self.knowledge_query.filter.return_value.first.return_value = SimpleNamespace(id="knowledge", workspace_id="ws")
        query = self.enterContext(patch("oss.serializers.file.QuerySet"))
        query.side_effect = lambda model: {
            User: self.user_query,
            Document: self.document_query,
            Knowledge: self.knowledge_query,
            WorkspaceUserResourcePermission: self.grants,
        }[model]
        self.enterContext(patch("oss.serializers.file.get_auth", return_value=self.auth))
        self.file = File(source_type=FileSourceType.DOCUMENT, source_id="document")

    def test_unassigned_custom_role_is_denied_without_a_type_error(self):
        self.auth.roles = {"EXTENDS_ADMIN"}
        with self.assertRaises(AppUnauthorizedFailed):
            _auth_system(self.file, "user")

    def test_explicit_view_and_manage_grants_allow_source_file_reads(self):
        self.grants.exists.return_value = True
        _auth_system(self.file, "user")
        self.grants.filter.assert_called_once_with(
            target="knowledge",
            workspace_id="ws",
            user_id="user",
            auth_target_type="KNOWLEDGE",
            permission_list__overlap=["VIEW", "MANAGE"],
        )

    def test_custom_workspace_manager_uses_the_permission_object(self):
        self.auth.roles = {"EXTENDS_WORKSPACE_MANAGE:w:ws"}
        self.auth.permissions = {"KNOWLEDGE_WORKSPACE_MANAGE:w:ws": PermissionConstants.KNOWLEDGE_READ.value.bit()}
        _auth_system(self.file, "user")
        self.grants.filter.assert_not_called()

    def test_workspace_role_grant_uses_the_target_workspace_permission(self):
        self.auth.roles = {"EXTENDS_USER:w:ws"}
        self.auth.permissions = {"KNOWLEDGE:w:ws": PermissionConstants.KNOWLEDGE_READ.value.bit()}
        self.grants.exists.return_value = True
        _auth_system(self.file, "user")
        self.assertIn("ROLE", self.grants.filter.call_args.kwargs["permission_list__overlap"])

    def test_another_workspace_permission_does_not_enable_role_grants(self):
        self.auth.permissions = {"KNOWLEDGE:w:other": PermissionConstants.KNOWLEDGE_READ.value.bit()}
        with self.assertRaises(AppUnauthorizedFailed):
            _auth_system(self.file, "user")
        self.assertNotIn("ROLE", self.grants.filter.call_args.kwargs["permission_list__overlap"])

    def test_workspace_manager_is_still_authorized(self):
        self.auth.roles = {"WORKSPACE_MANAGE:w:ws"}
        _auth_system(self.file, "user")
        self.grants.filter.assert_not_called()

    def test_application_read_permission_uses_the_same_typed_contract(self):
        self.auth.roles = {"EXTENDS_WORKSPACE_MANAGE:w:ws"}
        self.auth.permissions = {"APPLICATION_WORKSPACE_MANAGE:w:ws": PermissionConstants.APPLICATION_READ.value.bit()}
        _check_workspace_resource_permission(
            self.auth,
            "user",
            workspace_id="ws",
            target_id="application",
            auth_target_type="APPLICATION",
            read_permission=PermissionConstants.APPLICATION_READ.value,
        )
        self.grants.filter.assert_not_called()


class DirectFileDownloadPermissionTests(SimpleTestCase):
    def test_default_file_download_still_requires_file_authorization(self):
        file = SimpleNamespace(id="00000000-0000-0000-0000-000000000001", get_bytes=MagicMock())
        with patch("oss.serializers.file.QuerySet") as query, patch("oss.serializers.file.auth") as authorize:
            query.return_value.filter.return_value.first.return_value = file
            authorize.side_effect = AppUnauthorizedFailed(403, "denied")
            with self.assertRaises(AppUnauthorizedFailed):
                FileSerializer.Operate(data={"id": file.id, "with_file_auth": False}).get()
        authorize.assert_called_once_with(file, None)
        file.get_bytes.assert_not_called()
