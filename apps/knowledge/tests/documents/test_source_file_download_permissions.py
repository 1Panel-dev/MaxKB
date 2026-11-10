"""Source downloads use the authorized request while preserving file ownership checks."""

import json
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from django.test import TestCase
from django.urls import resolve
from rest_framework.test import APIRequestFactory, force_authenticate

from common.auth.constants.permission_constants import PermissionConstants
from common.auth.struct.auth import Auth
from common.exception.app_exception import AppUnauthorizedFailed
from knowledge.models import Document, DocumentResourceType, File, FileSourceType, Knowledge, KnowledgeType
from oss.serializers.file import FileSerializer


class WorkspaceSourceFileDownloadPermissionTests(TestCase):
    def setUp(self):
        self.knowledge = Knowledge.objects.create(
            name="Workflow source files", workspace_id="download-workspace", type=KnowledgeType.WORKFLOW
        )
        self.document = Document.objects.create(knowledge=self.knowledge, name="guide.txt", char_length=5)
        self.source = File(
            file_name="guide.txt", file_size=5, source_type=FileSourceType.DOCUMENT, source_id=str(self.document.id)
        )
        File.objects.bulk_create([self.source])
        self.document.meta = {"source_file_id": str(self.source.id)}
        self.document.save(update_fields=["meta"])
        self.read_bytes = self.enterContext(patch.object(File, "get_bytes", return_value=b"guide"))

    def download(self, *, workspace_id=None, document_id=None, roles=None, permission=None, cookie=None):
        workspace_id = workspace_id or self.knowledge.workspace_id
        path = (
            f"/workspace/{workspace_id}/knowledge/{self.knowledge.id}"
            f"/document/{document_id or self.document.id}/download_source_file"
        )
        request = APIRequestFactory().get(path)
        if cookie is not None:
            request.COOKIES["mk_file_auth"] = cookie
        permissions = {}
        if permission is not None:
            scoped = permission.get_workspace_knowledge_permission()(
                request, {"workspace_id": workspace_id, "knowledge_id": str(self.knowledge.id)}
            )
            permissions[scoped.get_resource_permission_key(scoped.resource_id)] = scoped.bit()
        force_authenticate(
            request,
            user=SimpleNamespace(id=str(uuid4()), type="TEST"),
            token=Auth(
                roles={f"WORKSPACE_MANAGE:w:{self.knowledge.workspace_id}"} if roles is None else roles,
                permissions=permissions,
            ),
        )
        match = resolve(path, urlconf="knowledge.urls")
        return match.func(request, **match.kwargs)

    def assert_downloaded(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"guide")
        self.assertIn("guide.txt", response["Content-Disposition"])

    def test_workspace_manager_downloads_documents_and_images_without_file_cookie(self):
        for resource_type in DocumentResourceType:
            with self.subTest(resource_type=resource_type):
                self.document.resource_type = resource_type
                self.document.save(update_fields=["resource_type"])
                self.assert_downloaded(self.download())

    @patch("oss.serializers.file.parse_file_token", return_value=None)
    def test_stale_file_cookie_does_not_override_current_request_authorization(self, parse_token):
        self.assert_downloaded(self.download(cookie="expired-test-token"))
        parse_token.assert_not_called()

    def test_explicit_download_grant_does_not_require_an_extra_read_grant(self):
        self.assert_downloaded(
            self.download(roles=set(), permission=PermissionConstants.KNOWLEDGE_DOCUMENT_DOWNLOAD_SOURCE_FILE)
        )

    def test_read_only_or_other_workspace_roles_cannot_download(self):
        for kwargs in (
            {"roles": set()},
            {"roles": {"WORKSPACE_MANAGE:w:another-workspace"}},
            {"roles": set(), "permission": PermissionConstants.KNOWLEDGE_DOCUMENT_READ},
        ):
            with self.subTest(kwargs=kwargs):
                response = self.download(**kwargs)
                self.assertEqual(response.status_code, 403)
        self.read_bytes.assert_not_called()

    def test_document_download_grant_does_not_allow_image_download(self):
        self.document.resource_type = DocumentResourceType.IMAGE
        self.document.save(update_fields=["resource_type"])
        response = self.download(roles=set(), permission=PermissionConstants.KNOWLEDGE_DOCUMENT_DOWNLOAD_SOURCE_FILE)
        self.assertEqual(response.status_code, 403)
        self.read_bytes.assert_not_called()
        self.assert_downloaded(
            self.download(roles=set(), permission=PermissionConstants.KNOWLEDGE_IMAGE_DOWNLOAD_SOURCE_FILE)
        )

    def test_workspace_and_document_ownership_remain_required(self):
        other_knowledge = Knowledge.objects.create(name="Other", workspace_id="other-workspace")
        other_document = Document.objects.create(knowledge=other_knowledge, name="other.txt", char_length=0)
        for kwargs in (
            {"workspace_id": other_knowledge.workspace_id, "roles": {"WORKSPACE_MANAGE:w:other-workspace"}},
            {"document_id": str(other_document.id)},
        ):
            with self.subTest(kwargs=kwargs):
                response = self.download(**kwargs)
                self.assertNotEqual(json.loads(response.content)["code"], 200)
        self.read_bytes.assert_not_called()

    def test_foreign_source_reference_does_not_expose_another_documents_file(self):
        other_document = Document.objects.create(knowledge=self.knowledge, name="other.txt", char_length=0)
        File.objects.filter(id=self.source.id).update(source_id=str(other_document.id))
        response = self.download()
        self.assertNotEqual(json.loads(response.content)["code"], 200)
        self.read_bytes.assert_not_called()

    def test_direct_file_access_still_requires_file_authentication(self):
        with self.assertRaises(AppUnauthorizedFailed):
            FileSerializer.Operate(data={"id": str(self.source.id)}).get()
        self.read_bytes.assert_not_called()
