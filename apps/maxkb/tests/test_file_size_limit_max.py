import unittest

from maxkb.conf import Config, ConfigManager

_UNSET = object()


class FileSizeLimitMaxTests(unittest.TestCase):
    def _config(self, raw=_UNSET):
        manager = ConfigManager(root_path="/tmp")
        if raw is not _UNSET:
            manager.from_mapping({"FILE_SIZE_LIMIT_MAX": raw})
        return manager.config

    def test_default_slider_cap_comes_from_config(self):
        """Knowledge-base upload slider max must be config, defaulting to 1000 MB."""
        self.assertEqual(Config.defaults.get("FILE_SIZE_LIMIT_MAX"), 1000)
        loaded = self._config()
        self.assertEqual(loaded.get("FILE_SIZE_LIMIT_MAX"), 1000)
        self.assertEqual(loaded.get_file_size_limit_max(), 1000)

    def test_env_style_string_is_read_as_int(self):
        # load_from_env stores MAXKB_* values as strings, same as from_mapping.
        loaded = self._config("4096")
        self.assertEqual(loaded.get_file_size_limit_max(), 4096)
        self.assertEqual(loaded.check_file_size_limit(1), 1)
        self.assertEqual(loaded.check_file_size_limit(4096), 4096)
        with self.assertRaises(ValueError):
            loaded.check_file_size_limit(4097)

    def test_whitespace_and_integral_float_are_accepted(self):
        self.assertEqual(self._config("  3000 ").get_file_size_limit_max(), 3000)
        self.assertEqual(self._config(1500).get_file_size_limit_max(), 1500)
        self.assertEqual(self._config(1500.0).get_file_size_limit_max(), 1500)

    def test_invalid_values_fall_back_to_default(self):
        for raw in ("nope", "", "0", "-3", "1.5", None, True, False, 0, -8):
            with self.subTest(raw=raw):
                self.assertEqual(self._config(raw).get_file_size_limit_max(), 1000)

    def test_value_above_integer_field_ceiling_is_clamped(self):
        loaded = self._config("999999999999")
        self.assertEqual(loaded.get_file_size_limit_max(), 2147483647)
        self.assertEqual(loaded.check_file_size_limit(2147483647), 2147483647)

    def test_knowledge_file_size_limit_rejects_out_of_range(self):
        loaded = self._config(500)
        for raw in (0, -1, 501, True, False, "500", None, 1.5):
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    loaded.check_file_size_limit(raw)
