import math

from django.db import transaction
from rest_framework import serializers

from knowledge.models import Knowledge
from maxkb.const import CONFIG


class StrictSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        if not isinstance(data, dict) or set(data) - set(self.fields):
            raise serializers.ValidationError("Invalid or unknown fields.")
        return super().to_internal_value(data)


class ExternalServiceSettings(StrictSerializer):
    enabled = serializers.BooleanField(required=False)
    authentication = serializers.BooleanField(required=False)

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("At least one setting is required.")
        return attrs


class RetrievalRequest(StrictSerializer):
    query_text = serializers.CharField(max_length=8000, allow_blank=False)
    top_number = serializers.IntegerField(default=5, min_value=1, max_value=50)
    similarity = serializers.FloatField(default=0.0, min_value=0.0, max_value=1.0)
    search_mode = serializers.ChoiceField(choices=["embedding", "keywords", "blend"], default="embedding")

    def to_internal_value(self, data):
        if isinstance(data, dict) and not isinstance(data.get("query_text"), str):
            raise serializers.ValidationError("query_text must be a string.")
        return super().to_internal_value(data)

    def validate_similarity(self, value):
        if not math.isfinite(value):
            raise serializers.ValidationError("similarity must be finite.")
        return value


def service_settings(knowledge, request=None):
    prefix = f"{CONFIG.get_chat_path()}/api/v3/knowledge/{knowledge.id}"
    absolute = request.build_absolute_uri if request else lambda path: path
    mcp_url = absolute(f"{prefix}/mcp")
    authentication = knowledge.external_service.get("authentication", False)
    connection = {"url": mcp_url, "transport": "streamable_http"}
    if authentication:
        connection["headers"] = {"Authorization": "Bearer <CHAT_USER_API_KEY>"}
    return {
        "enabled": knowledge.external_service.get("enabled", False),
        "authentication": authentication,
        "api_url": absolute(f"{prefix}/retrieve"),
        "mcp_url": mcp_url,
        "mcp_config": {f"knowledge_{knowledge.id}": connection},
    }


class ExternalServiceSerializer(serializers.Serializer):
    workspace_id = serializers.CharField()
    knowledge_id = serializers.UUIDField()

    def get_knowledge(self, lock=False):
        self.is_valid(raise_exception=True)
        query = Knowledge.objects.select_for_update() if lock else Knowledge.objects.all()
        knowledge = query.filter(
            id=self.validated_data["knowledge_id"], workspace_id=self.validated_data["workspace_id"]
        ).first()
        if knowledge is None:
            from common.exception.app_exception import NotFound404

            raise NotFound404(404, "Knowledge does not exist.")
        return knowledge

    def get_settings(self):
        return service_settings(self.get_knowledge(), self.context.get("request"))

    @transaction.atomic
    def update_settings(self, data):
        settings = ExternalServiceSettings(data=data)
        settings.is_valid(raise_exception=True)
        knowledge = self.get_knowledge(lock=True)
        knowledge.external_service = {**knowledge.external_service, **settings.validated_data}
        knowledge.save(update_fields=["external_service"])
        return service_settings(knowledge, self.context.get("request"))
