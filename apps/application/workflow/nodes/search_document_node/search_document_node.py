# coding=utf-8
"""
@project: MaxKB
@file： search_document_node.py
@desc:
"""

from typing import List

import jieba
from django.db.models import Q
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.workflow.common import WorkflowType
from application.workflow.i_node import INode
from common.auth.constants.role_constants import RoleConstants
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.utils.shared_resource_auth import filter_authorized_ids
from knowledge.models import Document, DocumentTag, Knowledge


class SearchDocumentNodeSerializer(serializers.Serializer):
    knowledge_id_list = serializers.ListField(
        required=False, child=serializers.UUIDField(required=True), label=_("knowledge id list"), default=list
    )
    search_mode = serializers.ChoiceField(
        required=False, choices=["auto", "custom"], label=_("search mode"), default="auto"
    )
    search_scope_type = serializers.ChoiceField(
        required=False,
        choices=["custom", "referencing"],
        label=_("search scope type"),
        allow_null=True,
        default="custom",
    )
    search_scope_source = serializers.ChoiceField(
        required=False, choices=["document", "knowledge"], label=_("search scope variable type"), default="knowledge"
    )
    search_scope_reference = serializers.ListField(required=False, label=_("search scope variable"), default=list)
    question_reference = serializers.ListField(required=False, label=_("question reference address"), default=list)
    search_condition_type = serializers.ChoiceField(
        required=False, choices=["AND", "OR"], label=_("search condition type"), default="AND"
    )
    search_condition_list = serializers.ListField(required=False, label=_("search condition list"), default=list)


def _handle_auto_tags(workflow_manage, document_id_list, question_reference):
    question = (
        workflow_manage.get_reference_field(question_reference[0], question_reference[1:]) if question_reference else ""
    )
    keywords = jieba.lcut(str(question))
    if not keywords:
        return set()

    q_objects = Q()
    for keyword in keywords:
        q_objects |= Q(tag__value__icontains=keyword)

    matched_doc_ids = set(
        QuerySet(DocumentTag)
        .filter(document_id__in=document_id_list)
        .filter(q_objects)
        .values_list("document_id", flat=True)
        .distinct()
    )
    return matched_doc_ids


def _handle_custom_tags(workflow_manage, document_id_list, search_condition_list, search_condition_type):
    if not search_condition_list:
        return set(document_id_list)

    if search_condition_type == "AND":
        matched_doc_ids = set(document_id_list)
        for condition in search_condition_list:
            tag_key = condition["key"]
            field_value = workflow_manage.generate_prompt(condition["value"])
            compare_type = condition["compare"]

            if not field_value or field_value == "None" or len(field_value) == 0:
                continue

            if compare_type == "not_contain":
                exclude_docs = set(
                    QuerySet(DocumentTag)
                    .filter(document_id__in=matched_doc_ids, tag__key=tag_key, tag__value__icontains=field_value)
                    .values_list("document_id", flat=True)
                    .distinct()
                )
                matched_doc_ids = matched_doc_ids - exclude_docs
            else:
                if compare_type == "contain":
                    q_filter = Q(tag__key=tag_key, tag__value__icontains=field_value)
                elif compare_type == "eq":
                    q_filter = Q(tag__key=tag_key, tag__value=field_value)
                else:
                    continue

                tag_docs = set(
                    QuerySet(DocumentTag)
                    .filter(document_id__in=matched_doc_ids)
                    .filter(q_filter)
                    .values_list("document_id", flat=True)
                    .distinct()
                )
                matched_doc_ids = matched_doc_ids.intersection(tag_docs)

        return matched_doc_ids
    else:
        matched_docs = set()
        for condition in search_condition_list:
            tag_key = condition["key"]
            field_value = workflow_manage.generate_prompt(condition["value"])
            compare_type = condition["compare"]

            if not field_value or field_value == "None" or len(field_value) == 0:
                continue

            if compare_type == "not_contain":
                exclude_docs = set(
                    QuerySet(DocumentTag)
                    .filter(document_id__in=document_id_list, tag__key=tag_key, tag__value__icontains=field_value)
                    .values_list("document_id", flat=True)
                    .distinct()
                )
                matched_docs = matched_docs.union(set(document_id_list) - exclude_docs)
            else:
                if compare_type == "contain":
                    q_filter = Q(tag__key=tag_key, tag__value__icontains=field_value)
                elif compare_type == "eq":
                    q_filter = Q(tag__key=tag_key, tag__value=field_value)
                else:
                    continue

                docs = set(
                    QuerySet(DocumentTag)
                    .filter(document_id__in=document_id_list)
                    .filter(q_filter)
                    .values_list("document_id", flat=True)
                    .distinct()
                )
                matched_docs = matched_docs.union(docs)

        return matched_docs


class SearchDocumentNode(INode):
    serializer_class = SearchDocumentNodeSerializer
    supported_workflow_type_list = [WorkflowType.APPLICATION, WorkflowType.TOOL]
    type = "search-document-node"

    def execute(self):
        node_params = self.get_parameters()
        workflow_params = self.get_workflow_parameters()

        knowledge_id_list = node_params.get("knowledge_id_list", [])
        search_mode = node_params.get("search_mode", "auto")
        search_scope_type = node_params.get("search_scope_type", "custom")
        search_scope_source = node_params.get("search_scope_source", "knowledge")
        search_scope_reference = node_params.get("search_scope_reference", [])
        question_reference = node_params.get("question_reference", [])
        search_condition_type = node_params.get("search_condition_type", "AND")
        search_condition_list = node_params.get("search_condition_list", [])

        workspace_id = workflow_params.get("workspace_id")

        if search_scope_type == "custom":
            knowledge_id_list = filter_authorized_ids("knowledge", knowledge_id_list, workspace_id)
            document_id_list = list(
                QuerySet(Document).filter(knowledge_id__in=knowledge_id_list).values_list("id", flat=True)
            )
        else:
            if search_scope_source == "document":
                document_id_list = (
                    self.workflow_manage.get_reference_field(search_scope_reference[0], search_scope_reference[1:])
                    if search_scope_reference
                    else []
                )
            else:
                ref_knowledge_ids = (
                    self.workflow_manage.get_reference_field(search_scope_reference[0], search_scope_reference[1:])
                    if search_scope_reference
                    else []
                )
                ref_knowledge_ids = filter_authorized_ids("knowledge", ref_knowledge_ids, workspace_id)
                document_id_list = list(
                    QuerySet(Document).filter(knowledge_id__in=ref_knowledge_ids).values_list("id", flat=True)
                )

        get_knowledge_list_of_authorized = DatabaseModelManage.get_model("get_knowledge_list_of_authorized")
        chat_user_type = workflow_params.get("chat_user_type")

        if get_knowledge_list_of_authorized is not None and RoleConstants.CHAT_USER.value.name == chat_user_type:
            actual_knowledge_ids = list(
                QuerySet(Document).filter(id__in=document_id_list).values_list("knowledge_id", flat=True).distinct()
            )
            authorized_knowledge_ids = get_knowledge_list_of_authorized(
                workflow_params.get("chat_user_id"), [str(k_id) for k_id in actual_knowledge_ids]
            )
            document_id_list = list(
                QuerySet(Document)
                .filter(id__in=document_id_list, knowledge_id__in=authorized_knowledge_ids)
                .values_list("id", flat=True)
            )

        if search_mode == "auto":
            matched_doc_ids = _handle_auto_tags(self.workflow_manage, document_id_list, question_reference)
            final_document_ids = list(matched_doc_ids)
        else:
            matched_document_ids = _handle_custom_tags(
                self.workflow_manage, document_id_list, search_condition_list, search_condition_type
            )
            final_document_ids = list(matched_document_ids)

        final_document_ids = [str(doc_id) for doc_id in final_document_ids]
        document_items = list(QuerySet(Document).filter(id__in=final_document_ids).values())
        final_knowledge_ids = list(set(str(doc["knowledge_id"]) for doc in document_items))
        knowledge_items = list(QuerySet(Knowledge).filter(id__in=final_knowledge_ids).values())

        self.write_context("document_list", final_document_ids)
        self.write_context("document_items", document_items)
        self.write_context("knowledge_list", final_knowledge_ids)
        self.write_context("knowledge_items", knowledge_items)

    def get_details(self, index: int = 0, position: dict = None, old_details: dict = None, **kwargs):
        details = super().get_details(index, position, old_details, **kwargs)
        details.update(
            {
                "document_list": self.get_context("document_list"),
                "document_items": self.get_context("document_items"),
                "knowledge_list": self.get_context("knowledge_list"),
                "knowledge_items": self.get_context("knowledge_items"),
            }
        )
        return details
