# coding=utf-8
"""
@project: MaxKB
@Author：虎虎虎
@file： search_knowledge_node.py
@date：2026/7/2 10:00
@desc:
"""

import os
import re
from typing import List, Dict

from django.core import validators
from django.db import connection
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.workflow.common import WorkflowType
from application.workflow.i_node import INode
from common.auth.constants.role_constants import RoleConstants
from common.config.embedding_config import VectorStore
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.db.search import native_search
from common.utils.common import flat_map, get_file_content
from common.utils.shared_resource_auth import filter_authorized_ids
from knowledge.models import Document, Paragraph, Knowledge, SearchMode
from maxkb.conf import PROJECT_DIR
from models_provider.tools import get_model_instance_by_model_workspace_id


class DatasetSettingSerializer(serializers.Serializer):
    top_n = serializers.IntegerField(required=True, label=_("Reference segment number"))
    similarity = serializers.FloatField(required=True, max_value=2, min_value=0, label=_("similarity"))
    search_mode = serializers.CharField(
        required=True,
        validators=[
            validators.RegexValidator(
                regex=re.compile("^embedding|keywords|blend$"),
                message=_("The type only supports embedding|keywords|blend"),
                code=500,
            )
        ],
        label=_("Retrieval Mode"),
    )
    max_paragraph_char_number = serializers.IntegerField(
        required=True, label=_("Maximum number of words in a quoted segment")
    )


class SearchKnowledgeNodeSerializer(serializers.Serializer):
    knowledge_id_list = serializers.ListField(
        required=True, child=serializers.UUIDField(required=True), label=_("Dataset id list")
    )
    knowledge_setting = DatasetSettingSerializer(required=True)
    question_reference_address = serializers.ListField(required=True)
    show_knowledge = serializers.BooleanField(
        required=True, label=_("The results are displayed in the knowledge sources")
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


def _get_paragraph_list(chat_record, node_id):
    return flat_map(
        [
            chat_record.details[key].get("paragraph_list", [])
            for key in chat_record.details
            if (chat_record.details[key].get("type", "") == "search-dataset-node")
            and chat_record.details[key].get("paragraph_list", []) is not None
            and key == node_id
        ]
    )


def _get_embedding_id(dataset_id_list):
    dataset_list = QuerySet(Knowledge).filter(id__in=dataset_id_list)
    if len(set([dataset.embedding_model_id for dataset in dataset_list])) > 1:
        raise Exception("关联知识库的向量模型不一致，无法召回分段。")
    if len(dataset_list) == 0:
        raise Exception("知识库设置错误,请重新设置知识库")
    return dataset_list[0].embedding_model_id


def _reset_title(title):
    if title is None or len(title.strip()) == 0:
        return ""
    else:
        return f"#### {title}\n"


def _reset_meta(meta):
    if not meta.get("allow_download", False):
        return {"allow_download": False}
    return meta


def _reset_paragraph(paragraph: Dict, embedding_list: List):
    filter_embedding_list = [
        embedding for embedding in embedding_list if str(embedding.get("paragraph_id")) == str(paragraph.get("id"))
    ]
    if filter_embedding_list is not None and len(filter_embedding_list) > 0:
        find_embedding = filter_embedding_list[-1]
        return {
            **paragraph,
            "similarity": find_embedding.get("similarity"),
            "is_hit_handling_method": find_embedding.get("similarity") > paragraph.get("directly_return_similarity")
            and paragraph.get("hit_handling_method") == "directly_return",
            "update_time": paragraph.get("update_time").strftime("%Y-%m-%d %H:%M:%S"),
            "create_time": paragraph.get("create_time").strftime("%Y-%m-%d %H:%M:%S"),
            "id": str(paragraph.get("id")),
            "knowledge_id": str(paragraph.get("knowledge_id")),
            "document_id": str(paragraph.get("document_id")),
            "meta": _reset_meta(paragraph.get("meta")),
        }


def _list_paragraph(embedding_list: List, vector):
    paragraph_id_list = [row.get("paragraph_id") for row in embedding_list]
    if paragraph_id_list is None or len(paragraph_id_list) == 0:
        return []
    paragraph_list = native_search(
        QuerySet(Paragraph).filter(id__in=paragraph_id_list),
        get_file_content(
            os.path.join(PROJECT_DIR, "apps", "application", "sql", "list_knowledge_paragraph_by_paragraph_id.sql")
        ),
        with_table_name=True,
    )
    if len(paragraph_list) != len(paragraph_id_list):
        exist_paragraph_list = [row.get("id") for row in paragraph_list]
        for paragraph_id in paragraph_id_list:
            if paragraph_id not in exist_paragraph_list:
                vector.delete_by_paragraph_id(paragraph_id)
    return paragraph_list


class SearchKnowledgeNode(INode):
    serializer_class = SearchKnowledgeNodeSerializer
    supported_workflow_type_list = [WorkflowType.APPLICATION, WorkflowType.TOOL]
    type = "search-knowledge-node"

    def execute(self):
        node_params = self.get_parameters()
        workflow_params = self.get_workflow_parameters()

        knowledge_id_list = node_params.get("knowledge_id_list", [])
        knowledge_setting = node_params.get("knowledge_setting", {})
        question_reference_address = node_params.get("question_reference_address", [])
        show_knowledge = node_params.get("show_knowledge", False)
        search_scope_type = node_params.get("search_scope_type", "custom")
        search_scope_source = node_params.get("search_scope_source", "knowledge")
        search_scope_reference = node_params.get("search_scope_reference", [])

        question = str(
            self.workflow_manage.get_reference_field(question_reference_address[0], question_reference_address[1:])
        )

        exclude_paragraph_id_list = []
        if workflow_params.get("re_chat", False):
            history_chat_record = workflow_params.get("history_chat_record", [])
            paragraph_id_list = [
                p.get("id")
                for p in flat_map(
                    [
                        _get_paragraph_list(chat_record, self.get_node_id())
                        for chat_record in history_chat_record
                        if chat_record.problem_text == question
                    ]
                )
            ]
            exclude_paragraph_id_list = list(set(paragraph_id_list))

        self.write_context("question", question)
        self.write_context("show_knowledge", show_knowledge)

        document_id_list = None
        if search_scope_type == "referencing":
            if search_scope_source == "knowledge":
                knowledge_id_list = self._get_reference_content(search_scope_reference)
            else:
                document_id_list = self._get_reference_content(search_scope_reference)
                knowledge_id_list = [
                    str(k)
                    for k in QuerySet(Document)
                    .filter(id__in=document_id_list)
                    .values_list("knowledge_id", flat=True)
                    .distinct()
                ]

        get_knowledge_list_of_authorized = DatabaseModelManage.get_model("get_knowledge_list_of_authorized")
        chat_user_type = workflow_params.get("chat_user_type")
        if get_knowledge_list_of_authorized is not None and RoleConstants.CHAT_USER.value.name == chat_user_type:
            knowledge_id_list = get_knowledge_list_of_authorized(workflow_params.get("chat_user_id"), knowledge_id_list)

        workspace_id = workflow_params.get("workspace_id")
        knowledge_id_list = filter_authorized_ids("knowledge", knowledge_id_list, workspace_id)

        if len(knowledge_id_list) == 0:
            self._write_empty_result(question)
            return

        model_id = _get_embedding_id(knowledge_id_list)
        self._check_cancelled()
        embedding_model = get_model_instance_by_model_workspace_id(model_id, workspace_id)
        embedding_value = embedding_model.embed_query(question)
        vector = VectorStore.get_embedding_vector()

        exclude_document_id_list = [
            str(document.id)
            for document in QuerySet(Document).filter(knowledge_id__in=knowledge_id_list, is_active=False)
        ]

        self._check_cancelled()
        embedding_list = vector.query(
            question,
            embedding_value,
            knowledge_id_list,
            document_id_list,
            exclude_document_id_list,
            exclude_paragraph_id_list,
            True,
            knowledge_setting.get("top_n"),
            knowledge_setting.get("similarity"),
            SearchMode(knowledge_setting.get("search_mode")),
        )

        connection.close()

        if embedding_list is None:
            self._write_empty_result(question)
            return

        paragraph_list = _list_paragraph(embedding_list, vector)
        result = [_reset_paragraph(paragraph, embedding_list) for paragraph in paragraph_list]
        result = sorted(result, key=lambda p: p.get("similarity"), reverse=True)

        self.write_context("paragraph_list", result)
        self.write_context("is_hit_handling_method_list", [row for row in result if row.get("is_hit_handling_method")])
        self.write_context(
            "data",
            "\n".join(
                [f"{_reset_title(paragraph.get('title', ''))}{paragraph.get('content')}" for paragraph in result]
            )[0 : knowledge_setting.get("max_paragraph_char_number", 5000)],
        )
        self.write_context(
            "directly_return",
            "\n".join([paragraph.get("content") for paragraph in result if paragraph.get("is_hit_handling_method")]),
        )

    def _write_empty_result(self, question):
        self.write_context("paragraph_list", [])
        self.write_context("is_hit_handling_method_list", [])
        self.write_context("data", "")
        self.write_context("directly_return", "")
        self.write_context("question", question)

    def _get_reference_content(self, fields: List[str]):
        if fields:
            return self.workflow_manage.get_reference_field(fields[0], fields[1:])
        return None

    def get_details(self, index: int = 0, position: dict = None, old_details: dict = None, **kwargs):
        details = super().get_details(index, position, old_details, **kwargs)
        details.update(
            {
                "question": self.get_context("question"),
                "paragraph_list": self.get_context("paragraph_list"),
                "data": self.get_context("data"),
                "show_knowledge": self.get_context("show_knowledge"),
            }
        )
        return details
