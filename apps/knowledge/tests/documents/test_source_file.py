"""Download the document's source even when older image attachments exist."""

from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from common.exception.app_exception import AppApiException
from knowledge.models import Document, File, FileSourceType, Knowledge
from knowledge.serializers.document import DocumentSerializers


DOCUMENT_ID = "00000000-0000-0000-0000-000000000001"
SOURCE_FILE_ID = "00000000-0000-0000-0000-000000000002"
KNOWLEDGE_ID = "00000000-0000-0000-0000-000000000003"
LEGACY_FILE_ID = "00000000-0000-0000-0000-000000000004"


class DocumentSourceFileTests(SimpleTestCase):
    def setUp(self):
        stack = ExitStack()
        self.addCleanup(stack.close)
        self.documents = MagicMock()
        self.documents.filter.return_value.values_list.return_value.first.return_value = SOURCE_FILE_ID
        self.files = MagicMock()
        self.document_files = self.files.filter.return_value
        self.source = SimpleNamespace(id=SOURCE_FILE_ID)
        self.document_files.filter.return_value.first.return_value = self.source
        query = stack.enter_context(patch("knowledge.serializers.document.QuerySet"))
        query.side_effect = lambda model: {Document: self.documents, File: self.files, Knowledge: MagicMock()}[model]
        self.download = stack.enter_context(patch("knowledge.serializers.document.FileSerializer.Operate"))
        self.download.return_value.get.return_value = "downloaded source"
        self.serializer = DocumentSerializers.Operate(data={"document_id": DOCUMENT_ID, "knowledge_id": KNOWLEDGE_ID})
        self.auth = object()

    def test_download_prefers_the_referenced_source_over_an_older_image_attachment(self):
        self.document_files.first.return_value = SimpleNamespace(id="older-image")

        self.assertEqual(self.serializer.download_source_file(self.auth), "downloaded source")

        self.files.filter.assert_called_once_with(source_id=DOCUMENT_ID, source_type=FileSourceType.DOCUMENT)
        self.document_files.filter.assert_called_once_with(id=SOURCE_FILE_ID)
        self.document_files.first.assert_not_called()
        self.download.assert_called_once_with(data={"id": SOURCE_FILE_ID})
        self.download.return_value.get.assert_called_once_with(mk_file_auth=self.auth, with_valid=True)

    def test_legacy_documents_without_a_reference_still_download_their_associated_file(self):
        self.documents.filter.return_value.values_list.return_value.first.return_value = None
        self.document_files.first.return_value = self.source

        self.serializer.download_source_file(self.auth)

        self.document_files.filter.assert_not_called()
        self.download.assert_called_once_with(data={"id": SOURCE_FILE_ID})

    def test_legacy_copied_sources_still_work_when_the_copy_has_a_different_id(self):
        self.document_files.filter.return_value.first.return_value = None
        self.document_files.first.return_value = SimpleNamespace(id=LEGACY_FILE_ID)

        self.serializer.download_source_file(self.auth)

        self.download.assert_called_once_with(data={"id": LEGACY_FILE_ID})

    def test_missing_source_does_not_attempt_a_file_download(self):
        self.document_files.filter.return_value.first.return_value = None
        self.document_files.first.return_value = None

        with self.assertRaises(AppApiException):
            self.serializer.download_source_file(self.auth)

        self.download.assert_not_called()

    def test_document_must_belong_to_the_requested_knowledge_before_download(self):
        self.documents.filter.return_value.exists.return_value = False

        with self.assertRaises(AppApiException):
            self.serializer.download_source_file(self.auth)

        self.files.filter.assert_not_called()
        self.download.assert_not_called()
