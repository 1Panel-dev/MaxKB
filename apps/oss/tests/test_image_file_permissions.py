from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIRequestFactory

from common.auth.constants.permission_constants import PermissionConstants
from common.constants.authentication_type import AuthenticationType
from common.exception.app_exception import AppUnauthorizedFailed
from knowledge.models import Document, DocumentResourceType, File, FileSourceType, Knowledge, Paragraph
from oss.serializers.file import _auth_system
from oss.views.file import FileRetrievalView
from system_manage.models import WorkspaceUserResourcePermission
from users.models import User


class ImageFilePermissionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="image-file-reader", password="!", role="USER")
        self.knowledge = Knowledge.objects.create(name="Image permissions", workspace_id="image-workspace")
        self.document = Document.objects.create(
            knowledge=self.knowledge, name="image.png", char_length=0, resource_type=DocumentResourceType.IMAGE
        )
        self.paragraph = Paragraph.objects.create(knowledge=self.knowledge, document=self.document, content="image")
        self.auth = SimpleNamespace(
            roles={"EXTENDS_WORKSPACE_MANAGE:w:image-workspace"},
            permissions={
                "KNOWLEDGE_WORKSPACE_MANAGE:w:image-workspace": PermissionConstants.KNOWLEDGE_IMAGE_READ.value.bit(),
            },
        )
        self.enterContext(patch("oss.serializers.file.get_auth", return_value=self.auth))
        self.file = File(source_type=FileSourceType.DOCUMENT, source_id=str(self.document.id), file_name="image.png")

    def test_image_reader_can_read_thumbnail_and_image_paragraph_files(self):
        for file in (self.file, File(source_type=FileSourceType.PARAGRAPH, source_id=str(self.paragraph.id))):
            with self.subTest(source_type=file.source_type):
                _auth_system(file, str(self.user.id))

    def test_thumbnail_http_response_returns_image_content(self):
        # Store only metadata; isolate object storage while keeping HTTP and permission evaluation real.
        File.objects.bulk_create([self.file])
        request = APIRequestFactory().get(f"/oss/file/{self.file.id}")
        request.COOKIES["mk_file_auth"] = "test-file-session"
        with (
            patch("oss.serializers.file.CONFIG.get", return_value="1"),
            patch(
                "oss.serializers.file.parse_file_token",
                return_value=SimpleNamespace(type=AuthenticationType.SYSTEM_USER, id=str(self.user.id)),
            ),
            patch.object(File, "get_bytes", return_value=b"\x89PNG\r\n\x1a\n") as read_bytes,
        ):
            response = FileRetrievalView.as_view()(request, file_id=str(self.file.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/png")
        self.assertEqual(response.content, b"\x89PNG\r\n\x1a\n")
        read_bytes.assert_called_once()

    def test_image_permission_from_another_workspace_is_denied(self):
        self.auth.roles = {"EXTENDS_WORKSPACE_MANAGE:w:other-workspace"}
        with self.assertRaises(AppUnauthorizedFailed):
            _auth_system(self.file, str(self.user.id))

    def test_image_permission_does_not_grant_document_file_reads(self):
        self.document.resource_type = DocumentResourceType.DOCUMENT
        self.document.save(update_fields=["resource_type"])
        with self.assertRaises(AppUnauthorizedFailed):
            _auth_system(self.file, str(self.user.id))

    def test_image_permission_does_not_grant_file_deletion(self):
        with self.assertRaises(AppUnauthorizedFailed):
            _auth_system(self.file, str(self.user.id), allow_content_read=False)

    def test_custom_user_requires_matching_knowledge_role_grant(self):
        self.auth.roles = {"EXTENDS_USER:w:image-workspace"}
        self.auth.permissions = {"KNOWLEDGE:w:image-workspace": PermissionConstants.KNOWLEDGE_IMAGE_READ.value.bit()}
        with self.assertRaises(AppUnauthorizedFailed):
            _auth_system(self.file, str(self.user.id))
        WorkspaceUserResourcePermission.objects.create(
            workspace_id=self.knowledge.workspace_id,
            user_id=self.user.id,
            target=self.knowledge.id,
            auth_target_type="KNOWLEDGE",
            permission_list=["ROLE"],
        )
        _auth_system(self.file, str(self.user.id))
