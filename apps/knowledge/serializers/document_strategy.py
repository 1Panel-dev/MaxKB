"""Request serializers for document processing strategies."""

import re
from urllib.parse import urlsplit

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from knowledge.services.document_strategy import normalize_document_strategy


class WebSourceURLField(serializers.CharField):
    """HTTP(S) URL field that also accepts single-label intranet hosts."""

    default_error_messages = {"invalid": _("Enter a valid HTTP or HTTPS URL")}

    def to_internal_value(self, data):
        value = super().to_internal_value(data).strip()
        parsed = urlsplit(value)
        if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
            self.fail("invalid")
        return value


class DocumentSplitStrategySerializer(serializers.Serializer):
    mode = serializers.ChoiceField(choices=["smart", "advanced"], required=False)
    patterns = serializers.ListField(child=serializers.CharField(allow_blank=False), required=False, allow_null=True)
    min_length = serializers.IntegerField(min_value=0, max_value=100000, required=False)
    max_length = serializers.IntegerField(min_value=50, max_value=100000, required=False)
    child_length = serializers.IntegerField(min_value=50, max_value=2048, required=False)
    auto_clean = serializers.BooleanField(required=False)

    def validate_patterns(self, patterns):
        if patterns is None:
            return None
        for pattern in patterns:
            try:
                re.compile(pattern)
            except re.error as exc:
                raise serializers.ValidationError(
                    _("Invalid paragraph identifier: {error}").format(error=str(exc))
                ) from exc
        return patterns

    def validate(self, attrs):
        minimum = attrs.get("min_length", 0)
        maximum = attrs.get("max_length", 4096)
        if minimum > maximum:
            raise serializers.ValidationError(
                {"min_length": _("The minimum paragraph length cannot exceed the maximum paragraph length")}
            )
        if "patterns" in attrs and "mode" not in attrs:
            attrs["mode"] = "advanced"
        if attrs.get("mode") == "smart" and attrs.get("patterns") is not None:
            raise serializers.ValidationError(
                {"patterns": _("Paragraph identifiers are only supported in advanced split mode")}
            )
        return attrs


class DocumentVisualStrategySerializer(serializers.Serializer):
    enabled = serializers.BooleanField(required=False)
    strategy = serializers.ChoiceField(choices=["model", "tool"], required=False)
    model_id = serializers.UUIDField(required=False, allow_null=True)
    tool_id = serializers.UUIDField(required=False, allow_null=True)

    def validate(self, attrs):
        if not attrs.get("enabled", False):
            return attrs
        strategy = attrs.get("strategy", "model")
        selected = attrs.get("model_id") if strategy == "model" else attrs.get("tool_id")
        if selected is None:
            field = "model_id" if strategy == "model" else "tool_id"
            raise serializers.ValidationError({field: _("This field is required when visual enhancement is enabled")})
        return attrs


class DocumentIndexStrategySerializer(serializers.Serializer):
    title_as_question = serializers.BooleanField(required=False)


class DocumentStrategySerializer(serializers.Serializer):
    split = DocumentSplitStrategySerializer(required=False)
    visual = DocumentVisualStrategySerializer(required=False)
    index = DocumentIndexStrategySerializer(required=False)

    def validate(self, attrs):
        try:
            return normalize_document_strategy(attrs)
        except (TypeError, ValueError) as exc:
            raise serializers.ValidationError(str(exc)) from exc


class DocumentSyncStrategySerializer(serializers.Serializer):
    strategy_mode = serializers.ChoiceField(choices=["default", "custom"], required=False, default="default")
    doc_strategy = DocumentStrategySerializer(required=False, allow_null=True)

    def validate(self, attrs):
        if attrs.get("strategy_mode") == "custom" and attrs.get("doc_strategy") is None:
            raise serializers.ValidationError(
                {"doc_strategy": _("This field is required when the custom document strategy is selected")}
            )
        return attrs
