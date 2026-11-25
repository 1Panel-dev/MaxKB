import threading
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from common.exception.app_exception import AppApiException
from users.serializers import user as user_serializer
from users.serializers.user import RePasswordSerializer


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "user-password-reset-tests",
        }
    }
)
class PasswordResetConcurrencyTests(SimpleTestCase):
    def setUp(self):
        user_serializer.cache.clear()

    def test_incorrect_code_does_not_consume_reset_code(self):
        email = "reset-wrong-code@example.com"
        code = "271828"
        code_cache_key = user_serializer.get_key(f"{email}:reset_password")
        user_serializer.cache.set(code_cache_key, code, version=user_serializer.version)

        with self.assertRaises(AppApiException):
            user_serializer.check_verify_code_attempts(email, "reset_password", "000000", consume=True)

        self.assertEqual(user_serializer.cache.get(code_cache_key, version=user_serializer.version), code)
        self.assertTrue(user_serializer.check_verify_code_attempts(email, "reset_password", code, consume=True))

    def test_reset_code_can_only_be_consumed_by_one_concurrent_request(self):
        email = "reset-race@example.com"
        code = "314159"
        concurrency = 8
        code_cache_key = user_serializer.get_key(f"{email}:reset_password")
        user_serializer.cache.set(code_cache_key, code, version=user_serializer.version)

        updates = []

        class RecordingUserQuerySet:
            def __init__(self, *args, **kwargs):
                pass

            def filter(self, **kwargs):
                return self

            def update(self, **kwargs):
                updates.append(kwargs)
                return 1

        barrier = threading.Barrier(concurrency)
        original_get = user_serializer.cache.get

        def synchronized_get(key, default=None, version=None):
            value = original_get(key, default=default, version=version)
            if key == code_cache_key:
                barrier.wait(timeout=5)
            return value

        def attempt(index):
            password = f"RaceP!{index:06d}"
            serializer = RePasswordSerializer(
                data={
                    "email": email,
                    "code": code,
                    "password": password,
                    "re_password": password,
                }
            )
            try:
                return serializer.reset_password()
            except AppApiException:
                return False

        with (
            patch.object(user_serializer, "QuerySet", RecordingUserQuerySet),
            patch.object(user_serializer.cache, "get", side_effect=synchronized_get),
            ThreadPoolExecutor(max_workers=concurrency) as executor,
        ):
            results = list(executor.map(attempt, range(concurrency)))

        self.assertEqual(results.count(True), 1)
        self.assertEqual(len(updates), 1)
