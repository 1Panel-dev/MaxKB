"""Request and response serializers for external knowledge synchronization."""

from functools import partial

from common.db.search import page_search
from common.exception.app_exception import AppApiException
from common.result import Page
from django.db import transaction
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from knowledge.models import Knowledge, KnowledgeSyncLog, KnowledgeSyncType
from knowledge.services.knowledge_sync_schedule import (
    SCHEDULED_KNOWLEDGE_TYPES,
    deploy_knowledge_sync_job,
    normalize_knowledge_sync_setting,
)


class KnowledgeSyncSettingRequest(serializers.Serializer):
    enabled = serializers.BooleanField(required=True, label=_("Enable scheduled synchronization"))
    schedule_type = serializers.ChoiceField(
        required=True,
        choices=["daily", "cron"],
        label=_("Schedule type"),
    )
    time = serializers.RegexField(
        required=False,
        regex=r"^([01]\d|2[0-3]):([0-5]\d)$",
        label=_("Daily synchronization time"),
    )
    cron_expression = serializers.CharField(required=False, allow_blank=False, label=_("Cron expression"))
    sync_type = serializers.ChoiceField(
        required=True,
        choices=KnowledgeSyncType.choices,
        label=_("Synchronization type"),
    )

    def validate(self, attrs):
        if attrs["schedule_type"] == "daily" and not attrs.get("time"):
            raise serializers.ValidationError({"time": _("This field is required for a daily schedule")})
        if attrs["schedule_type"] == "cron" and not attrs.get("cron_expression"):
            raise serializers.ValidationError({"cron_expression": _("This field is required for a Cron schedule")})
        try:
            return normalize_knowledge_sync_setting(attrs)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc


class KnowledgeSyncSettingOperationSerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=True, label=_("workspace id"))
    knowledge_id = serializers.UUIDField(required=True, label=_("knowledge id"))

    def validate(self, attrs):
        knowledge = (
            QuerySet(Knowledge)
            .filter(
                id=attrs["knowledge_id"],
                workspace_id=attrs["workspace_id"],
                type__in=SCHEDULED_KNOWLEDGE_TYPES,
            )
            .first()
        )
        if knowledge is None:
            raise AppApiException(404, _("Scheduled synchronization is not supported for this knowledge base"))
        attrs["knowledge"] = knowledge
        return attrs

    def get_setting(self):
        self.is_valid(raise_exception=True)
        return normalize_knowledge_sync_setting((self.validated_data["knowledge"].meta or {}).get("sync_setting"))

    def update_setting(self, setting):
        self.is_valid(raise_exception=True)
        setting_serializer = KnowledgeSyncSettingRequest(data=setting)
        setting_serializer.is_valid(raise_exception=True)
        knowledge_id = self.validated_data["knowledge"].id
        with transaction.atomic():
            knowledge = QuerySet(Knowledge).select_for_update().get(id=knowledge_id)
            knowledge.meta = {**(knowledge.meta or {}), "sync_setting": setting_serializer.validated_data}
            knowledge.save(update_fields=["meta", "update_time"])
            transaction.on_commit(partial(deploy_knowledge_sync_job, str(knowledge.id)))
        return setting_serializer.validated_data


class KnowledgeSyncLogSerializer(serializers.ModelSerializer):
    duration_seconds = serializers.SerializerMethodField()

    class Meta:
        model = KnowledgeSyncLog
        fields = [
            "id",
            "create_time",
            "update_time",
            "sync_type",
            "trigger_type",
            "status",
            "total_count",
            "synced_count",
            "skipped_count",
            "deleted_count",
            "failed_count",
            "duration_ms",
            "duration_seconds",
            "message",
        ]

    def get_duration_seconds(self, instance):
        return round(instance.duration_ms / 1000, 3)


class KnowledgeSyncLogQuerySerializer(KnowledgeSyncSettingOperationSerializer):
    def page(self, current_page, page_size):
        self.is_valid(raise_exception=True)
        query_set = (
            QuerySet(KnowledgeSyncLog).filter(knowledge_id=self.validated_data["knowledge"].id).order_by("-create_time")
        )
        page = page_search(
            current_page,
            page_size,
            query_set,
            lambda item: KnowledgeSyncLogSerializer(item).data,
        )
        return Page(page["total"], page["records"], page["current"], page["size"])
