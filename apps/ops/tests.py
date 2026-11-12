import importlib.util
import os
import unittest
from pathlib import Path
from unittest.mock import patch


class HmacSignedSerializerTest(unittest.TestCase):
    module_path = Path(__file__).resolve().parent / 'celery' / 'hmac_signed_serializer.py'

    def load_serializer(self):
        spec = importlib.util.spec_from_file_location('hmac_signed_serializer_test', self.module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_default_secret_is_a_string_and_round_trips(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop('MAXKB_HMAC_SIGNED_SERIALIZER_SECRET_KEY', None)
            os.environ.pop('MAXKB_SECRET_KEY', None)
            serializer = self.load_serializer()

        self.assertIsInstance(serializer._local_secret_key, str)
        payload = serializer.secure_dumps({'task': 'demo'})
        self.assertEqual(serializer.secure_loads(payload), {'task': 'demo'})

    def test_explicit_shared_secret_is_used(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop('MAXKB_HMAC_SIGNED_SERIALIZER_SECRET_KEY', None)
            os.environ['MAXKB_SECRET_KEY'] = 'shared-test-secret'
            serializer = self.load_serializer()

        self.assertEqual(serializer._local_secret_key, 'shared-test-secret')
        payload = serializer.secure_dumps({'task': 'demo'})
        self.assertEqual(serializer.secure_loads(payload), {'task': 'demo'})


if __name__ == '__main__':
    unittest.main()
