from django.test import SimpleTestCase
from django.urls import resolve

from maxkb.const import CONFIG
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
