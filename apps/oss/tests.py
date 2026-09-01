from unittest import mock

from django.test import SimpleTestCase
from django.urls import resolve

from common.exception.app_exception import AppUnauthorizedFailed
from knowledge.models import FileSourceType
from maxkb.const import CONFIG
from oss.serializers.file import auth
from oss.views import FileRetrievalView, FileView, GetUrlView


class OssUrlTestCase(SimpleTestCase):
    def assert_resolves(self, path, view_class, namespace, kwargs=None):
        match = resolve(path)

        self.assertIs(match.func.view_class, view_class)
        self.assertEqual(match.namespace, namespace)
        self.assertEqual(match.kwargs, kwargs or {})

    def test_file_api_routes_use_unique_namespaces(self):
        self.assert_resolves(
            f'{CONFIG.get_admin_path()}/api/oss/file',
            FileView,
            'admin_oss',
        )
        self.assert_resolves(
            f'{CONFIG.get_chat_path()}/api/oss/file',
            FileView,
            'chat_oss',
        )

    def test_file_retrieval_routes_use_unique_namespaces(self):
        self.assert_resolves(
            f'{CONFIG.get_admin_path()}/oss/file/file-id',
            FileRetrievalView,
            'admin_oss_retrieval',
            {'file_id': 'file-id'},
        )
        self.assert_resolves(
            f'{CONFIG.get_chat_path()}/oss/file/file-id',
            FileRetrievalView,
            'chat_oss_retrieval',
            {'file_id': 'file-id'},
        )

    def test_get_url_retrieval_routes_pass_application_id(self):
        self.assert_resolves(
            f'{CONFIG.get_admin_path()}/oss/get_url/application-id',
            GetUrlView,
            'admin_oss_retrieval',
            {'application_id': 'application-id'},
        )
        self.assert_resolves(
            f'{CONFIG.get_chat_path()}/oss/get_url/application-id',
            GetUrlView,
            'chat_oss_retrieval',
            {'application_id': 'application-id'},
        )


class FileAuthTestCase(SimpleTestCase):
    """Regression tests for anonymous retrieval of APPLICATION-source files."""

    @staticmethod
    def _make_file(source_type, source_id, meta=None):
        file = mock.Mock()
        file.id = 'f0000000-0000-0000-0000-000000000001'
        file.source_type = source_type
        file.source_id = source_id
        file.meta = meta or {}
        return file

    def test_application_file_without_token_is_denied(self):
        """A visitor-created APPLICATION file with no chat_id must not be publicly retrievable."""
        file = self._make_file(FileSourceType.APPLICATION, 'application-1')
        with mock.patch('oss.serializers.file.CONFIG', {'FILE_AUTH': '1'}), \
                mock.patch('oss.serializers.file.QuerySet') as qs:
            qs.return_value.filter.return_value.exists.return_value = False
            with self.assertRaises(AppUnauthorizedFailed):
                auth(file, None)

    def test_public_temporary_file_does_not_require_token(self):
        """Temporary/public source types remain anonymously retrievable."""
        file = self._make_file(FileSourceType.TEMPORARY_120_MINUTE, FileSourceType.TEMPORARY_120_MINUTE.value)
        with mock.patch('oss.serializers.file.CONFIG', {'FILE_AUTH': '1'}):
            # It should return without raising.
            self.assertIsNone(auth(file, None))


class FileUploadPermissionTestCase(SimpleTestCase):
    """The /oss/file upload endpoint must not let chat/anon clients bind files to protected sources."""

    @staticmethod
    def _chat_request(source_type, source_id):
        request = mock.Mock()
        request.user = None
        request.auth = mock.Mock()
        request.auth.chat_user_id = 'chat-user-1'
        request.data = {'source_type': source_type, 'source_id': source_id}
        request.FILES = {'file': mock.Mock()}
        request.META = {}
        request.path = '/chat/api/oss/file'
        request.query_params = {}
        return request

    def test_chat_upload_binding_to_application_is_denied(self):
        request = self._chat_request(FileSourceType.APPLICATION.value, 'application-1')
        with mock.patch('common.log.log.Log'):
            with self.assertRaises(AppUnauthorizedFailed):
                FileView().post(request)

    def test_chat_upload_binding_to_chat_is_allowed(self):
        request = self._chat_request(FileSourceType.CHAT.value, 'chat-1')
        with mock.patch('common.log.log.Log'), \
                mock.patch('oss.views.file.QuerySet') as qs, \
                mock.patch('oss.views.file.FileSerializer') as serializer_cls:
            qs.return_value.filter.return_value.first.return_value = mock.Mock()
            serializer_cls.return_value.upload.return_value = './oss/file/1'
            response = FileView().post(request)
        self.assertEqual(response.status_code, 200)

    def test_chat_upload_binding_to_foreign_chat_is_denied(self):
        request = self._chat_request(FileSourceType.CHAT.value, 'foreign-chat')
        with mock.patch('common.log.log.Log'), \
                mock.patch('oss.views.file.QuerySet') as qs:
            qs.return_value.filter.return_value.first.return_value = None
            with self.assertRaises(AppUnauthorizedFailed):
                FileView().post(request)

    def test_system_user_upload_binding_to_application_is_allowed(self):
        request = mock.Mock()
        request.user = mock.Mock()
        request.user.id = 'user-1'
        request.data = {'source_type': FileSourceType.APPLICATION.value, 'source_id': 'application-1'}
        request.FILES = {'file': mock.Mock()}
        request.META = {}
        request.path = '/admin/api/oss/file'
        request.query_params = {}
        with mock.patch('common.log.log.Log'), \
                mock.patch('oss.views.file.FileSerializer') as serializer_cls:
            serializer_cls.return_value.upload.return_value = './oss/file/1'
            response = FileView().post(request)
        self.assertEqual(response.status_code, 200)

    def test_logged_in_user_on_chat_path_cannot_bind_to_application(self):
        """Even a logged-in user must not bind files to protected sources via the /chat path."""
        request = mock.Mock()
        request.user = mock.Mock()
        request.user.id = 'user-1'
        request.data = {'source_type': FileSourceType.APPLICATION.value, 'source_id': 'application-1'}
        request.FILES = {'file': mock.Mock()}
        request.META = {}
        request.path = '/chat/api/oss/file'
        request.query_params = {}
        with mock.patch('common.log.log.Log'):
            with self.assertRaises(AppUnauthorizedFailed):
                FileView().post(request)
