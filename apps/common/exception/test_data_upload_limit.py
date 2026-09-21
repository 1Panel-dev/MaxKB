# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： test_data_upload_limit.py
    @date：2026/9/22
    @desc: DATA_UPLOAD_MAX_MEMORY_SIZE default and RequestDataTooBig handling (#7062)
"""
import ast
import json
import logging
import os
import sys
import unittest
from pathlib import Path

APPS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if APPS_DIR not in sys.path:
    sys.path.insert(0, APPS_DIR)

os.environ.setdefault("MAXKB_CONFIG", "1")
os.environ.setdefault("MAXKB_CONFIG_TYPE", "ENV")
os.environ.setdefault("MAXKB_DB_NAME", "maxkb")

import django  # noqa: E402
from django.conf import settings  # noqa: E402

if not settings.configured:
    settings.configure(
        SECRET_KEY="test-secret",
        DEBUG=False,
        USE_I18N=True,
        USE_TZ=True,
        LANGUAGE_CODE="en",
        LANGUAGES=[("en", "English")],
        LOCALE_PATHS=[],
        INSTALLED_APPS=["rest_framework"],
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    )
    django.setup()

from django.core.exceptions import RequestDataTooBig, SuspiciousOperation  # noqa: E402

from common.exception.handle_exception import handle_exception  # noqa: E402
from maxkb.conf import Config, ConfigManager  # noqa: E402

logging.getLogger("max_kb").addHandler(logging.NullHandler())
logging.getLogger("max_kb").propagate = False

UPLOAD_HINT = "MAXKB_DATA_UPLOAD_MAX_MEMORY_SIZE"
MIN_UPLOAD_BYTES = 100 * 1024 * 1024
SETTINGS_FILES = (
    os.path.join(APPS_DIR, "maxkb", "settings", "base", "web.py"),
    os.path.join(APPS_DIR, "maxkb", "settings", "base", "model.py"),
)


def _settings_upload_limit(path, values):
    """Evaluate the DATA_UPLOAD_MAX_MEMORY_SIZE assignment in a settings module."""
    tree = ast.parse(Path(path).read_text(encoding="utf-8"), filename=path)
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        names = [target.id for target in node.targets if isinstance(target, ast.Name)]
        if "DATA_UPLOAD_MAX_MEMORY_SIZE" not in names:
            continue
        expression = ast.Expression(node.value)
        ast.fix_missing_locations(expression)

        class _Config:
            @staticmethod
            def get(key, default=None):
                if key in values:
                    return values[key]
                return default

        return eval(compile(expression, path, "eval"), {"CONFIG": _Config, "int": int})
    raise AssertionError(f"DATA_UPLOAD_MAX_MEMORY_SIZE is not assigned in {path}")


def _response_body(response):
    return json.loads(response.content.decode())


def _po_field(block, field):
    lines = []
    capture = False
    for line in block.splitlines():
        if line.startswith(field + " ") or line == field:
            capture = True
            rest = line[len(field):].strip()
            lines = [ast.literal_eval(rest)] if rest else []
            continue
        if capture:
            if line.startswith('"'):
                lines.append(ast.literal_eval(line.strip()))
            else:
                break
    return "".join(lines)


def _po_pair(path):
    text = Path(path).read_text(encoding="utf-8")
    marker = "Request body exceeded DATA_UPLOAD_MAX_MEMORY_SIZE."
    for block in text.split("\n\n"):
        if marker not in block or "msgid" not in block:
            continue
        return _po_field(block, "msgid"), _po_field(block, "msgstr")
    raise AssertionError(f"{path} is missing the upload-limit message")


UPLOAD_MESSAGE = (
    "Request body exceeded DATA_UPLOAD_MAX_MEMORY_SIZE. "
    "Increase MAXKB_DATA_UPLOAD_MAX_MEMORY_SIZE (environment variable) "
    "or DATA_UPLOAD_MAX_MEMORY_SIZE (config file), in bytes."
)


class DataUploadLimitTests(unittest.TestCase):
    def test_config_default_is_at_least_100_mib(self):
        self.assertGreaterEqual(Config.defaults["DATA_UPLOAD_MAX_MEMORY_SIZE"], MIN_UPLOAD_BYTES)
        manager = ConfigManager(root_path=APPS_DIR)
        self.assertGreaterEqual(int(manager.config.get("DATA_UPLOAD_MAX_MEMORY_SIZE")), MIN_UPLOAD_BYTES)

    def test_file_mapping_overrides_default(self):
        manager = ConfigManager(root_path=APPS_DIR)
        manager.from_mapping({"DATA_UPLOAD_MAX_MEMORY_SIZE": 42 * 1024 * 1024})
        self.assertEqual(int(manager.config.get("DATA_UPLOAD_MAX_MEMORY_SIZE")), 42 * 1024 * 1024)

    def test_env_name_overrides_default(self):
        key = "MAXKB_DATA_UPLOAD_MAX_MEMORY_SIZE"
        previous = os.environ.get(key)
        os.environ[key] = "209715200"
        try:
            manager = ConfigManager(root_path=APPS_DIR)
            manager.load_from_env()
            self.assertEqual(int(manager.config.get("DATA_UPLOAD_MAX_MEMORY_SIZE")), 209715200)
        finally:
            if previous is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = previous

    def test_web_and_model_settings_use_config_limit(self):
        for path in SETTINGS_FILES:
            default_limit = _settings_upload_limit(path, dict(Config.defaults))
            self.assertGreaterEqual(default_limit, MIN_UPLOAD_BYTES)
            override = _settings_upload_limit(path, {"DATA_UPLOAD_MAX_MEMORY_SIZE": "3145728"})
            self.assertEqual(override, 3145728)

    def test_request_data_too_big_returns_config_hint(self):
        exc = RequestDataTooBig("Request body exceeded settings.DATA_UPLOAD_MAX_MEMORY_SIZE.")
        response = handle_exception(exc, {})
        body = _response_body(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["code"], 500)
        self.assertEqual(body["message"], UPLOAD_MESSAGE)
        self.assertIn(UPLOAD_HINT, body["message"])

    def test_suspicious_operation_with_upload_message_returns_config_hint(self):
        exc = SuspiciousOperation("Request body exceeded settings.DATA_UPLOAD_MAX_MEMORY_SIZE.")
        body = _response_body(handle_exception(exc, {}))
        self.assertIn(UPLOAD_HINT, body["message"])
        self.assertIn("DATA_UPLOAD_MAX_MEMORY_SIZE", body["message"])

    def test_catalogs_translate_the_upload_limit_message(self):
        locale_dir = os.path.join(APPS_DIR, "locales")
        en_msgid, en_msgstr = _po_pair(os.path.join(locale_dir, "en_US", "LC_MESSAGES", "django.po"))
        zh_msgid, zh_msgstr = _po_pair(os.path.join(locale_dir, "zh_CN", "LC_MESSAGES", "django.po"))
        hant_msgid, hant_msgstr = _po_pair(os.path.join(locale_dir, "zh_Hant", "LC_MESSAGES", "django.po"))
        self.assertEqual(en_msgid, UPLOAD_MESSAGE)
        self.assertEqual(zh_msgid, UPLOAD_MESSAGE)
        self.assertEqual(hant_msgid, UPLOAD_MESSAGE)
        self.assertEqual(en_msgstr, "")
        self.assertIn("MAXKB_DATA_UPLOAD_MAX_MEMORY_SIZE", zh_msgstr)
        self.assertIn("DATA_UPLOAD_MAX_MEMORY_SIZE", zh_msgstr)
        self.assertIn("MAXKB_DATA_UPLOAD_MAX_MEMORY_SIZE", hant_msgstr)
        self.assertNotEqual(zh_msgstr, hant_msgstr)

    def test_other_suspicious_operation_is_not_rewritten(self):
        exc = SuspiciousOperation("Invalid HTTP_HOST header")
        body = _response_body(handle_exception(exc, {}))
        self.assertEqual(body["message"], "Invalid HTTP_HOST header")
        self.assertNotIn(UPLOAD_HINT, body["message"])


if __name__ == "__main__":
    unittest.main()
