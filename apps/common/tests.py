import builtins
import importlib
import os
import sys
from unittest import TestCase
from unittest.mock import patch


class ToolCodeImportTest(TestCase):
    def test_imports_when_unix_only_modules_are_unavailable(self):
        original_import = builtins.__import__

        def import_without_unix_only_modules(name, *args, **kwargs):
            if name in {"pwd", "resource"}:
                raise ModuleNotFoundError(f"No module named '{name}'")
            return original_import(name, *args, **kwargs)

        env = {
            "MAXKB_CONFIG_TYPE": "ENV",
            "DJANGO_SETTINGS_MODULE": "maxkb.settings",
        }

        original_module = sys.modules.pop("common.utils.tool_code", None)
        try:
            with patch.dict(os.environ, env), patch.object(
                builtins, "__import__", side_effect=import_without_unix_only_modules
            ):
                importlib.import_module("common.utils.tool_code")
        finally:
            sys.modules.pop("common.utils.tool_code", None)
            if original_module is not None:
                sys.modules["common.utils.tool_code"] = original_module
