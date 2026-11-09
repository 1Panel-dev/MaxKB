from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase

from common.auth.constants.permission_constants import PermissionConstants
from common.exception.app_exception import AppUnauthorizedFailed
from knowledge.models import Document, DocumentResourceType, File, FileSourceType, Knowledge, Paragraph
from oss.serializers.file import _auth_system
from system_manage.models import WorkspaceUserResourcePermission
from users.models import User


class DocumentFilePermissionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="document-file-reader", password="!", role="USER")
        self.knowledge = Knowledge.objects.create(name="Document permissions", workspace_id="document-workspace")
        self.document = Document.objects.create(knowledge=self.knowledge, name="with-images.docx", char_length=0)
        self.paragraph = Paragraph.objects.create(knowledge=self.knowledge, document=self.document, content="image")
        self.auth = SimpleNamespace(
            roles={"EXTENDS_WORKSPACE_MANAGE:w:document-workspace"},
            permissions={
                "KNOWLEDGE_WORKSPACE_MANAGE:w:document-workspace": PermissionConstants.KNOWLEDGE_DOCUMENT_READ.value.bit(),
            },
        )
        self.enterContext(patch("oss.serializers.file.get_auth", return_value=self.auth))

    def files(self):
        return [
            File(source_type=source_type, source_id=str(source_id))
            for source_type, source_id in (
                (FileSourceType.KNOWLEDGE, self.knowledge.id),
                (FileSourceType.DOCUMENT, self.document.id),
                (FileSourceType.PARAGRAPH, self.paragraph.id),
            )
        ]

    def test_inherited_manager_can_read_preview_source_and_inline_images(self):
        for file in self.files():
            with self.subTest(source_type=file.source_type):
                _auth_system(file, str(self.user.id))

    def test_document_read_in_another_workspace_does_not_grant_access(self):
        self.auth.roles = {"EXTENDS_WORKSPACE_MANAGE:w:another-workspace"}
        for file in self.files():
            with self.subTest(source_type=file.source_type), self.assertRaises(AppUnauthorizedFailed):
                _auth_system(file, str(self.user.id))

    def test_document_reader_does_not_gain_standalone_image_access(self):
        self.document.resource_type = DocumentResourceType.IMAGE
        self.document.save(update_fields=["resource_type"])
        for file in self.files()[1:]:
            with self.subTest(source_type=file.source_type), self.assertRaises(AppUnauthorizedFailed):
                _auth_system(file, str(self.user.id))

    def test_content_read_permission_does_not_expand_file_delete_permission(self):
        with self.assertRaises(AppUnauthorizedFailed):
            _auth_system(self.files()[1], str(self.user.id), allow_content_read=False)

    def test_custom_user_needs_role_grant_for_the_target_knowledge(self):
        self.auth.roles = {"EXTENDS_USER:w:document-workspace"}
        self.auth.permissions = {
            "KNOWLEDGE:w:document-workspace": PermissionConstants.KNOWLEDGE_DOCUMENT_READ.value.bit()
        }
        file = self.files()[-1]
        with self.assertRaises(AppUnauthorizedFailed):
            _auth_system(file, str(self.user.id))
        WorkspaceUserResourcePermission.objects.create(
            workspace_id=self.knowledge.workspace_id,
            user_id=self.user.id,
            target=self.knowledge.id,
            auth_target_type="KNOWLEDGE",
            permission_list=["ROLE"],
        )
        _auth_system(file, str(self.user.id))

    def test_document_create_permission_alone_does_not_allow_read(self):
        self.auth.permissions = {
            "KNOWLEDGE_WORKSPACE_MANAGE:w:document-workspace": PermissionConstants.KNOWLEDGE_DOCUMENT_CREATE.value.bit()
        }
        with self.assertRaises(AppUnauthorizedFailed):
            _auth_system(self.files()[1], str(self.user.id))
