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


class MissingLargeObjectTests(SimpleTestCase):
    """#7356: metadata exists but Postgres large object is gone → 404, not 500."""

    def test_operate_get_maps_missing_large_object_to_404(self):
        from unittest.mock import MagicMock, patch

        from django.db import DatabaseError

        from common.exception.app_exception import NotFound404
        from oss.serializers.file import FileSerializer

        operate = FileSerializer.Operate(data={'id': '00000000-0000-0000-0000-000000000001'})
        self.assertTrue(operate.is_valid())

        fake_file = MagicMock()
        fake_file.file_name = 'pic.png'
        fake_file.get_bytes.side_effect = DatabaseError('large object 90563 does not exist')

        with patch('oss.serializers.file.QuerySet') as qs, patch('oss.serializers.file.auth'):
            qs.return_value.filter.return_value.first.return_value = fake_file
            with self.assertRaises(NotFound404) as ctx:
                operate.get(with_valid=False)
        self.assertEqual(ctx.exception.status_code, 404)

    def test_operate_get_rethrows_unrelated_database_error(self):
        from unittest.mock import MagicMock, patch

        from django.db import DatabaseError

        from oss.serializers.file import FileSerializer

        operate = FileSerializer.Operate(data={'id': '00000000-0000-0000-0000-000000000001'})
        self.assertTrue(operate.is_valid())

        fake_file = MagicMock()
        fake_file.file_name = 'pic.png'
        fake_file.get_bytes.side_effect = DatabaseError('connection already closed')

        with patch('oss.serializers.file.QuerySet') as qs, patch('oss.serializers.file.auth'):
            qs.return_value.filter.return_value.first.return_value = fake_file
            with self.assertRaises(DatabaseError):
                operate.get(with_valid=False)
