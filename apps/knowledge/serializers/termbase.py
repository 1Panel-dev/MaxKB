from typing import Dict, List

import uuid_utils.compat as uuid
from common.db.search import page_search
from common.exception.app_exception import AppApiException
from django.db import transaction
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from knowledge.models import Knowledge, Termbase


class TermbaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Termbase
        fields = ["id", "content", "knowledge_id", "create_time", "update_time"]


class TermbaseInstanceSerializer(serializers.Serializer):
    id = serializers.CharField(required=False, label=_("termbase id"))
    content = serializers.CharField(required=True, max_length=256, label=_("content"))


class TermbaseBatchSerializer(serializers.Serializer):
    termbase_list = serializers.ListField(
        required=True,
        label=_("termbase list"),
        child=serializers.CharField(required=True, max_length=256, label=_("content")),
    )


class TermbaseSerializers(serializers.Serializer):
    class BatchOperate(serializers.Serializer):
        workspace_id = serializers.CharField(required=True, label=_("workspace id"))
        knowledge_id = serializers.UUIDField(required=True, label=_("knowledge id"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            workspace_id = self.data.get("workspace_id")
            query_set = QuerySet(Knowledge).filter(id=self.data.get("knowledge_id"))
            if workspace_id:
                query_set = query_set.filter(workspace_id=workspace_id)
            if not query_set.exists():
                raise AppApiException(500, _("Knowledge id does not exist"))

        def delete(self, problem_id_list: List, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            QuerySet(Termbase).filter(id__in=problem_id_list).delete()
            return True

        def export(self, problem_id_list: List, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            terms = (
                QuerySet(Termbase)
                .filter(id__in=problem_id_list)
                .order_by("-create_time")
                .values_list("content", flat=True)
            )
            return "\n".join(terms)

    class Operate(serializers.Serializer):
        workspace_id = serializers.CharField(required=True, label=_("workspace id"))
        knowledge_id = serializers.UUIDField(required=True, label=_("knowledge id"))
        termbase_id = serializers.UUIDField(required=True, label=_("termbase id"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            workspace_id = self.data.get("workspace_id")
            query_set = QuerySet(Knowledge).filter(id=self.data.get("knowledge_id"))
            if workspace_id:
                query_set = query_set.filter(workspace_id=workspace_id)
            if not query_set.exists():
                raise AppApiException(500, _("Knowledge id does not exist"))

        def one(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            return TermbaseInstanceSerializer(QuerySet(Termbase).get(**{"id": self.data.get("termbase_id")})).data

        @transaction.atomic
        def delete(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            QuerySet(Termbase).filter(id=self.data.get("termbase_id")).delete()
            return True

        @transaction.atomic
        def edit(self, instance: Dict, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            termbase_id = self.data.get("termbase_id")
            knowledge_id = self.data.get("knowledge_id")
            content = instance.get("content")
            termbase = QuerySet(Termbase).filter(id=termbase_id, knowledge_id=knowledge_id).first()
            if termbase:
                termbase.content = content
                termbase.save()

    class Create(serializers.Serializer):
        workspace_id = serializers.CharField(required=True, label=_("workspace id"))
        knowledge_id = serializers.UUIDField(required=True, label=_("knowledge id"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            workspace_id = self.data.get("workspace_id")
            query_set = QuerySet(Knowledge).filter(id=self.data.get("knowledge_id"))
            if workspace_id:
                query_set = query_set.filter(workspace_id=workspace_id)
            if not query_set.exists():
                raise AppApiException(500, _("Knowledge id does not exist"))

        def batch(self, termbase_list, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                TermbaseBatchSerializer(data={"termbase_list": termbase_list}).is_valid(raise_exception=True)
            termbase_list = list(set(termbase_list))
            knowledge_id = self.data.get("knowledge_id")
            exists_termbase_content_list = [
                termbase.content
                for termbase in QuerySet(Termbase).filter(knowledge_id=knowledge_id, content__in=termbase_list)
            ]
            termbase_instance_list = [
                Termbase(id=uuid.uuid7(), knowledge_id=knowledge_id, content=problem_content)
                for problem_content in termbase_list
                if (
                    not exists_termbase_content_list.__contains__(problem_content)
                    if len(exists_termbase_content_list) > 0
                    else True
                )
            ]

            QuerySet(Termbase).bulk_create(termbase_instance_list) if len(termbase_instance_list) > 0 else None
            return [TermbaseSerializer(termbase_instance).data for termbase_instance in termbase_instance_list]

    class Query(serializers.Serializer):
        workspace_id = serializers.CharField(required=True, label=_("workspace id"))
        knowledge_id = serializers.UUIDField(required=True, label=_("knowledge id"))
        content = serializers.CharField(required=False, label=_("content"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            workspace_id = self.data.get("workspace_id")
            query_set = QuerySet(Knowledge).filter(id=self.data.get("knowledge_id"))
            if workspace_id:
                query_set = query_set.filter(workspace_id=workspace_id)
            if not query_set.exists():
                raise AppApiException(500, _("Knowledge id does not exist"))

        def get_query_set(self):
            self.is_valid()
            query_set = QuerySet(model=Termbase)
            query_set = query_set.filter(**{"knowledge_id": self.data.get("knowledge_id")})
            if "content" in self.data:
                query_set = query_set.filter(**{"content__icontains": self.data.get("content")})
            query_set = query_set.order_by("-create_time")
            return query_set

        def list(self):
            query_set = self.get_query_set()
            return TermbaseSerializer(query_set, many=True).data

        def page(self, current_page, page_size):
            query_set = self.get_query_set()
            return page_search(current_page, page_size, query_set, lambda r: TermbaseSerializer(r).data)
