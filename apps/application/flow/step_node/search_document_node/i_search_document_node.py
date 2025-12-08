# coding=utf-8
from typing import Type, List

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.flow.i_step_node import INode, NodeResult


class SearchDocumentStepNodeSerializer(serializers.Serializer):
    knowledge_id_list = serializers.ListField(
        required=False, child=serializers.UUIDField(required=True),
        label=_("knowledge id list"), default=list
    )
    search_mode = serializers.ChoiceField(
        required=False, choices=['auto', 'custom'], label=_("search mode"), default='auto'
    )
    search_scope_type = serializers.ChoiceField(
        required=False, choices=['custom', 'referencing'], label=_("search scope type"),
        allow_null=True, default='custom'
    )
    search_scope_source = serializers.ChoiceField(
        required=False, choices=['document', 'knowledge'],
        label=_("search scope variable type"), default='knowledge'
    )
    search_scope_reference = serializers.ListField(
        required=False, label=_("search scope variable"), default=list
    )
    question_reference = serializers.ListField(
        required=False, label=_("question reference address"), default=list
    )
    search_condition_type = serializers.ChoiceField(
        required=False, choices=['AND', 'OR'], label=_("search condition type"), default='AND'
    )
    search_condition_list = serializers.ListField(
        required=False, label=_("search condition list"), default=list
    )

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)


class ISearchDocumentStepNode(INode):
    type = 'search-document-node'

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return SearchDocumentStepNodeSerializer

    def _run(self):
        return self.execute(**self.node_params_serializer.data, **self.flow_params_serializer.data)

    def execute(self, knowledge_id_list: List, search_mode: str, search_scope_type: str, search_scope_source: str,
                search_scope_reference: List, question_reference: List, search_condition_type: str,
                search_condition_list: List,
                **kwargs) -> NodeResult:
        pass
