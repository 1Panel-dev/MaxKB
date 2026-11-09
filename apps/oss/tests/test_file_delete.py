import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from common.exception.app_exception import AppUnauthorizedFailed
from knowledge.models import FileSourceType
from oss.serializers.file import FileSerializer
from oss.views.file import FileView


class FileDeleteTests(SimpleTestCase):
    user_id = "00000000-0000-0000-0000-000000000001"
    file_id = "00000000-0000-0000-0000-000000000002"

    def setUp(self):
        self.file = SimpleNamespace(
            id=self.file_id,
            source_type=FileSourceType.TEMPORARY_120_MINUTE,
            meta={"user_id": self.user_id},
            delete=MagicMock(),
        )
        query = self.enterContext(patch("oss.serializers.file.QuerySet"))
        query.return_value.filter.return_value.first.return_value = self.file
        self.enterContext(patch("common.log.log.Log"))

    def test_scoped_inherited_roles_can_delete_their_own_upload_without_file_cookie(self):
        for role in ("EXTENDS_WORKSPACE_MANAGE:w:workspace", "EXTENDS_USER:w:workspace", "ADMIN"):
            with self.subTest(role=role):
                request = APIRequestFactory().delete(f"/oss/file/{self.file_id}")
                force_authenticate(
                    request,
                    user=SimpleNamespace(id=self.user_id, type="TEST"),
                    token=SimpleNamespace(roles=[role], permissions={}),
                )
                response = FileView.Operate.as_view()(request, file_id=self.file_id)
                self.assertEqual(json.loads(response.content)["code"], 200)
        self.assertEqual(self.file.delete.call_count, 3)

    def test_temporary_file_owned_by_another_user_or_without_owner_is_not_deleted(self):
        for owner in ("another-user", None):
            with self.subTest(owner=owner):
                self.file.meta = {"user_id": owner}
                with self.assertRaises(AppUnauthorizedFailed):
                    FileSerializer.Operate(data={"id": self.file_id}).delete(user_id=self.user_id)
        self.file.delete.assert_not_called()

    def test_nontemporary_file_keeps_existing_resource_authorization(self):
        self.file.source_type = FileSourceType.DOCUMENT
        with patch("oss.serializers.file.auth", side_effect=AppUnauthorizedFailed(403, "denied")) as authorize:
            with self.assertRaises(AppUnauthorizedFailed):
                FileSerializer.Operate(data={"id": self.file_id}).delete(
                    mk_file_auth="file-token", user_id=self.user_id
                )
        authorize.assert_called_once_with(self.file, "file-token")
        self.file.delete.assert_not_called()
