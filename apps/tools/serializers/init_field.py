# coding=utf-8
"""
    @project: MaxKB
    @file: init_field.py
    @desc: Validate declarative tool initialization fields.
"""
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from html import escape


INIT_FIELD_TYPES = (
    "TextInput", "TextareaInput", "JsonInput", "PasswordInput", "SingleSelect", "MultiSelect",
    "RadioCard", "RadioRow", "MultiRow", "Slider", "SwitchInput", "DatePicker", "UploadInput",
    "Model", "Knowledge", "TreeSelect",
)
RULE_KEYS = {"required", "type", "min", "max", "len", "enum", "pattern", "whitespace", "message", "trigger"}
ATTR_KEYS = {
    "maxlength", "minlength", "show-word-limit", "rows", "type", "show-password",
    "min", "max", "step", "precision", "show-input-controls", "show-input", "format", "value-format",
    "accept", "limit", "multiple", "data", "filterable", "provider_list", "knowledge_list",
    "placeholder", "disabled", "clearable", "style", "class",
}
LEGACY_JSON_VALIDATOR = (
    "validator = (rule, value, callback) => { "
    "return componentFormRef.value?.validate_rules(rule, value, callback); }"
)


def is_json_validator(input_type, value):
    return (
        input_type == "JsonInput"
        and isinstance(value, str)
        and "".join(value.split()) == "".join(LEGACY_JSON_VALIDATOR.split())
    )


class InitField(serializers.Serializer):
    field = serializers.CharField(required=True, label=_("field name"))
    label = serializers.JSONField(required=True, label=_("field label"))
    required = serializers.BooleanField(required=True, label=_("required"))
    input_type = serializers.ChoiceField(choices=INIT_FIELD_TYPES, label=_("input type"))
    default_value = serializers.JSONField(required=False, allow_null=True)
    show_default_value = serializers.BooleanField(required=False, default=False)
    props_info = serializers.DictField(required=False, default=dict)
    attrs = serializers.DictField(required=False, default=dict)
    option_list = serializers.ListField(child=serializers.DictField(), required=False)
    text_field = serializers.CharField(required=False, allow_blank=True)

    def to_internal_value(self, data):
        validated = super().to_internal_value(data)
        # Preserve declarative metadata such as options and reference assignments.
        return {**data, **{key: value for key, value in validated.items() if key in data}}

    def validate_label(self, value):
        if isinstance(value, str):
            return value
        if isinstance(value, dict) and value.get("input_type") == "TooltipLabel":
            attrs = value.get("attrs", {})
            if (
                isinstance(value.get("label"), str)
                and isinstance(attrs, dict)
                and not attrs.keys() - {"tooltip"}
                and isinstance(attrs.get("tooltip", ""), str)
                and not value.get("relation_trigger_field_dict")
            ):
                return {"input_type": "TooltipLabel", "label": value["label"], "attrs": attrs, "props_info": {}}
        raise serializers.ValidationError(_("Unsupported field label"))

    def validate(self, data):
        if data.get("relation_trigger_field_dict"):
            raise serializers.ValidationError(_("Tool initialization fields cannot contain request scripts"))
        attrs = data.get("attrs", {})
        if attrs.keys() - ATTR_KEYS:
            raise serializers.ValidationError(_("Unsupported field attributes"))
        if "provider_list" in attrs:
            providers = attrs["provider_list"]
            if not isinstance(providers, list) or any(not isinstance(provider, dict) for provider in providers):
                raise serializers.ValidationError(_("Model providers must be a list of objects"))
            data["attrs"] = {**attrs, "provider_list": [
                {**provider, "model_form_field": validate_init_field_list(provider["model_form_field"])}
                if "model_form_field" in provider else provider
                for provider in providers
            ]}
        props_info = data.get("props_info", {})
        rules = props_info.get("rules", [])
        if not isinstance(rules, list):
            raise serializers.ValidationError(_("Validation rules must be a list"))
        safe_rules = []
        for rule in rules:
            if not isinstance(rule, dict):
                raise serializers.ValidationError(_("Validation rules must be objects"))
            rule = dict(rule)
            if "validator" in rule:
                validator = rule.pop("validator")
                # Keep the old frontend compatible, but never return caller-supplied executable code.
                if not is_json_validator(data["input_type"], validator):
                    raise serializers.ValidationError(_("Executable validation rules are not supported"))
                rule["validator"] = LEGACY_JSON_VALIDATOR
            if rule.keys() - (RULE_KEYS | {"validator"}):
                raise serializers.ValidationError(_("Unsupported validation rule properties"))
            safe_rules.append(rule)
        if "rules" in props_info:
            data["props_info"] = {**props_info, "rules": safe_rules}
        return data


def validate_init_field_list(value):
    serializer = InitField(data=[] if value is None else value, many=True)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


def sanitize_init_field_list(value):
    """Filter historical configurations on reads without modifying stored tool parameters."""
    if not isinstance(value, list):
        return []
    fields = []
    for field in value:
        if not isinstance(field, dict):
            continue
        field = dict(field)
        field.pop("relation_trigger_field_dict", None)
        attrs = field.get("attrs", {})
        field["attrs"] = {key: val for key, val in attrs.items() if key in ATTR_KEYS} if isinstance(attrs, dict) else {}
        providers = field["attrs"].get("provider_list")
        if isinstance(providers, list):
            field["attrs"]["provider_list"] = [
                {**provider, "model_form_field": sanitize_init_field_list(provider["model_form_field"])}
                if "model_form_field" in provider else provider
                for provider in providers if isinstance(provider, dict)
            ]
        props_info = field.get("props_info", {})
        props_info = dict(props_info) if isinstance(props_info, dict) else {}
        if "rules" in props_info:
            rules = props_info["rules"]
            props_info["rules"] = []
            for rule in rules if isinstance(rules, list) else []:
                if not isinstance(rule, dict):
                    continue
                safe_rule = {key: val for key, val in rule.items() if key in RULE_KEYS}
                if is_json_validator(field.get("input_type"), rule.get("validator")):
                    safe_rule["validator"] = LEGACY_JSON_VALIDATOR
                props_info["rules"].append(safe_rule)
        field["props_info"] = props_info
        serializer = InitField(data=field)
        if serializer.is_valid():
            field = serializer.validated_data
            if field["input_type"] == "RadioCard":
                text_field = field.get("text_field") or "key"
                field["option_list"] = [
                    {**option, text_field: escape(option[text_field])}
                    if isinstance(option.get(text_field), str) else option
                    for option in field.get("option_list", [])
                ]
            fields.append(field)
    return fields


class InitFieldListField(serializers.JSONField):
    def to_representation(self, value):
        return sanitize_init_field_list(value)
