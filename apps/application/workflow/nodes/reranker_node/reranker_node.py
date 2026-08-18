# coding=utf-8
"""
@project: MaxKB
@file： reranker_node.py
@desc:
"""

from typing import List

from django.utils.translation import gettext_lazy as _
from langchain_core.documents import Document
from rest_framework import serializers

from application.workflow.common import WorkflowType
from application.workflow.i_node import INode
from models_provider.tools import get_model_instance_by_model_workspace_id


class RerankerSettingSerializer(serializers.Serializer):
    top_n = serializers.IntegerField(required=True, label=_("Reference segment number"))
    similarity = serializers.FloatField(required=True, max_value=2, min_value=0, label=_("Reference segment number"))
    max_paragraph_char_number = serializers.IntegerField(
        required=True, label=_("Maximum number of words in a quoted segment")
    )


class RerankerNodeSerializer(serializers.Serializer):
    reranker_setting = RerankerSettingSerializer(required=True)
    question_reference_address = serializers.ListField(required=True)
    reranker_model_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    reranker_model_id_type = serializers.CharField(required=False, default="custom")
    reranker_model_id_reference = serializers.ListField(required=False, child=serializers.CharField(), allow_empty=True)
    reranker_reference_list = serializers.ListField(required=True, child=serializers.ListField(required=True))
    show_knowledge = serializers.BooleanField(
        required=True, label=_("The results are displayed in the knowledge sources")
    )


def _merge_reranker_list(reranker_list, result=None):
    if result is None:
        result = []
    for document in reranker_list:
        if isinstance(document, list):
            _merge_reranker_list(document, result)
        elif isinstance(document, dict):
            content = document.get("title", "") + document.get("content", "")
            title = document.get("title")
            result.append(
                Document(
                    page_content=str(document) if len(content) == 0 else content, metadata={"title": title, **document}
                )
            )
        else:
            result.append(Document(page_content=str(document), metadata={}))
    return result


def _filter_result(document_list: List[Document], max_paragraph_char_number, top_n, similarity):
    use_len = 0
    result = []
    for index in range(len(document_list)):
        document = document_list[index]
        if (
            use_len >= max_paragraph_char_number
            or index >= top_n
            or document.metadata.get("relevance_score") < similarity
        ):
            break
        content = document.page_content[0 : max_paragraph_char_number - use_len]
        use_len = use_len + len(content)
        result.append({"page_content": content, "metadata": document.metadata})
    return result


def _reset_result_list(result_list: List[Document], document_list: List[Document]):
    r = []
    document_list = document_list.copy()
    for result in result_list:
        filter_result_list = [document for document in document_list if document.page_content == result.page_content]
        if len(filter_result_list) > 0:
            item = filter_result_list[0]
            document_list.remove(item)
            r.append(
                Document(
                    page_content=item.page_content,
                    metadata={**item.metadata, "relevance_score": result.metadata.get("relevance_score")},
                )
            )
        else:
            r.append(result)
    return r


def _reset_metadata(metadata):
    meta = metadata.get("meta")
    if isinstance(metadata.get("meta"), dict):
        if not meta.get("allow_download", False):
            metadata["meta"] = {"allow_download": False}
    return metadata


class RerankerNode(INode):
    serializer_class = RerankerNodeSerializer
    supported_workflow_type_list = [WorkflowType.APPLICATION, WorkflowType.TOOL]
    type = "reranker-node"

    def execute(self):
        node_params = self.get_parameters()
        workflow_params = self.get_workflow_parameters()

        question_ref = node_params.get("question_reference_address")
        reranker_reference_list = node_params.get("reranker_reference_list")
        reranker_setting = node_params.get("reranker_setting")
        reranker_model_id = node_params.get("reranker_model_id")
        reranker_model_id_type = node_params.get("reranker_model_id_type", "custom")
        reranker_model_id_reference = node_params.get("reranker_model_id_reference")
        show_knowledge = node_params.get("show_knowledge", False)

        question = self.workflow_manage.get_reference_field(question_ref[0], question_ref[1:])
        question = str(question)

        reranker_list = [self.workflow_manage.get_reference_field(ref[0], ref[1:]) for ref in reranker_reference_list]

        if reranker_model_id_type == "reference" and reranker_model_id_reference:
            reference_data = self.workflow_manage.get_reference_field(
                reranker_model_id_reference[0],
                reranker_model_id_reference[1:],
            )
            if reference_data and isinstance(reference_data, dict):
                reranker_model_id = reference_data.get(
                    "reranker_model_id", reference_data.get("model_id", reranker_model_id)
                )

        if not reranker_model_id:
            raise Exception(_("Model is not allowed to be empty"))

        self.write_context("show_knowledge", show_knowledge)

        documents = _merge_reranker_list(reranker_list)
        documents = [d for d in documents if d.page_content and len(d.page_content) > 0]

        if len(documents) == 0:
            self.write_context("document_list", [])
            self.write_context("question", question)
            self.write_context("result_list", [])
            self.write_context("result", "")
            return

        top_n = reranker_setting.get("top_n", 3)
        self.write_context(
            "document_list",
            [
                {"page_content": document.page_content, "metadata": _reset_metadata(document.metadata)}
                for document in documents
            ],
        )
        self.write_context("question", question)

        workspace_id = workflow_params.get("workspace_id")
        reranker_model = get_model_instance_by_model_workspace_id(reranker_model_id, workspace_id, top_n=top_n)

        self._check_cancelled()
        result = reranker_model.compress_documents(documents, question)

        similarity = reranker_setting.get("similarity", 0.6)
        max_paragraph_char_number = reranker_setting.get("max_paragraph_char_number", 5000)

        result = _reset_result_list(result, documents)
        r = _filter_result(result, max_paragraph_char_number, top_n, similarity)

        self.write_context("result_list", r)
        self.write_context("result", "".join([item.get("page_content") for item in r]))
        self.write_context(
            "is_hit_handling_method_list", [row for row in r if row.get("metadata").get("is_hit_handling_method")]
        )

    def get_details(self, index: int = 0, position: dict = None, old_details: dict = None, **kwargs):
        details = super().get_details(index, position, old_details, **kwargs)
        details.update(
            {
                "question": self.get_context("question"),
                "result_list": self.get_context("result_list"),
                "result": self.get_context("result"),
                "document_list": self.get_context("document_list"),
                "show_knowledge": self.get_context("show_knowledge"),
            }
        )
        return details
