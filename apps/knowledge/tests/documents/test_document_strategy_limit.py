"""The nested limit field works with existing strategy data and fingerprints."""

from django.test import SimpleTestCase
from knowledge.serializers.document_strategy import DocumentStrategySerializer
from knowledge.services.document_strategy import (
    normalize_document_strategy,
    parse_web_content,
    stable_hash,
    strategy_hashes,
)


class DocumentStrategyLimitTests(SimpleTestCase):
    def test_nested_limit_is_validated_and_retained(self):
        for limit in (50, 49523, 100000):
            with self.subTest(limit=limit):
                serializer = DocumentStrategySerializer(data={"split": {"limit": limit}})

                self.assertTrue(serializer.is_valid(), serializer.errors)
                self.assertEqual(serializer.validated_data["split"]["limit"], limit)
                self.assertEqual(serializer.validated_data["split"]["max_length"], limit)

    def test_invalid_nested_limits_are_rejected(self):
        for limit in (0, 49, 100001, None, "invalid", 50.5):
            with self.subTest(limit=limit):
                serializer = DocumentStrategySerializer(data={"split": {"limit": limit}})

                self.assertFalse(serializer.is_valid())
                self.assertIn("limit", serializer.errors["split"])

    def test_limit_takes_precedence_over_legacy_maximum_length(self):
        serializer = DocumentStrategySerializer(data={"split": {"limit": 8000, "max_length": 4096, "min_length": 5000}})

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["split"]["limit"], 8000)
        self.assertEqual(serializer.validated_data["split"]["max_length"], 8000)

    def test_minimum_length_is_checked_against_the_selected_limit(self):
        serializer = DocumentStrategySerializer(data={"split": {"limit": 500, "max_length": 4096, "min_length": 1000}})

        self.assertFalse(serializer.is_valid())
        self.assertIn("min_length", serializer.errors["split"])

    def test_legacy_strategies_expose_limit_for_form_backfill(self):
        strategy = normalize_document_strategy({"split": {"mode": "advanced", "max_length": 49523}})

        self.assertEqual(strategy["split"]["limit"], 49523)
        self.assertEqual(normalize_document_strategy(strategy), strategy)

    def test_renaming_the_limit_preserves_existing_split_fingerprints(self):
        legacy = {"split": {"mode": "advanced", "max_length": 49523}}
        current = {"split": {"mode": "advanced", "limit": 49523}}
        legacy_split = normalize_document_strategy(legacy)["split"]
        legacy_split.pop("limit")

        self.assertEqual(strategy_hashes(current), strategy_hashes(legacy))
        self.assertEqual(strategy_hashes(current)["split_strategy_hash"], stable_hash(legacy_split))
        self.assertNotEqual(strategy_hashes(current), strategy_hashes({"split": {"limit": 50, "mode": "advanced"}}))

    def test_web_parser_uses_nested_limit(self):
        paragraphs = parse_web_content("x" * 49623, {"split": {"mode": "advanced", "limit": 49523}})

        self.assertEqual([len(p["content"]) for p in paragraphs], [49523, 100])
