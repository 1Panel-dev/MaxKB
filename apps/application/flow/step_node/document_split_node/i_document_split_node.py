# coding=utf-8

from typing import Type

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.flow.common import WorkflowMode
from application.flow.i_step_node import INode, NodeResult


class DocumentSplitNodeSerializer(serializers.Serializer):
    document_list = serializers.ListField(required=False, label=_("document list"))
    split_strategy = serializers.ChoiceField(
        choices=['auto', 'custom', 'qa'], required=False, label=_("split strategy"), default='auto'
    )
    paragraph_title_relate_problem_type = serializers.ChoiceField(
        choices=['custom', 'referencing'], required=False, label=_("paragraph title relate problem type"),
        default='custom'
    )
    paragraph_title_relate_problem = serializers.BooleanField(
        required=False, label=_("paragraph title relate problem"), default=False
    )
    paragraph_title_relate_problem_reference = serializers.ListField(
        required=False, label=_("paragraph title relate problem reference"), child=serializers.CharField(), default=[]
    )
    document_name_relate_problem_type = serializers.ChoiceField(
        choices=['custom', 'referencing'], required=False, label=_("document name relate problem type"),
        default='custom'
    )
    document_name_relate_problem = serializers.BooleanField(
        required=False, label=_("document name relate problem"), default=False
    )
    document_name_relate_problem_reference = serializers.ListField(
        required=False, label=_("document name relate problem reference"), child=serializers.CharField(), default=[]
    )
    limit = serializers.IntegerField(required=False, label=_("limit"), default=4096)
    limit_type = serializers.ChoiceField(
        choices=['custom', 'referencing'], required=False, label=_("document name relate problem type"),
        default='custom'
    )
    limit_reference = serializers.ListField(
        required=False, label=_("limit reference"), child=serializers.CharField(), default=[]
    )
    chunk_size = serializers.IntegerField(required=False, label=_("chunk size"), default=256)
    chunk_size_type = serializers.ChoiceField(
        choices=['custom', 'referencing'], required=False, label=_("chunk size type"), default='custom'
    )
    chunk_size_reference = serializers.ListField(
        required=False, label=_("chunk size reference"), child=serializers.CharField(), default=[]
    )
    patterns = serializers.ListField(
        required=False, label=_("patterns"), child=serializers.CharField(), default=[]
    )
    patterns_type = serializers.ChoiceField(
        choices=['custom', 'referencing'], required=False, label=_("patterns type"), default='custom'
    )
    patterns_reference = serializers.ListField(
        required=False, label=_("patterns reference"), child=serializers.CharField(), default=[]
    )
    with_filter = serializers.BooleanField(
        required=False, label=_("with filter"), default=False
    )
    with_filter_type = serializers.ChoiceField(
        choices=['custom', 'referencing'], required=False, label=_("with filter type"), default='custom'
    )
    with_filter_reference = serializers.ListField(
        required=False, label=_("with filter reference"), child=serializers.CharField(), default=[]
    )


class IDocumentSplitNode(INode):
    type = 'document-split-node'
    support = [
        WorkflowMode.APPLICATION, WorkflowMode.APPLICATION_LOOP, WorkflowMode.KNOWLEDGE_LOOP, WorkflowMode.KNOWLEDGE
    ]

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return DocumentSplitNodeSerializer

    def _run(self):
        return self.execute(**self.node_params_serializer.data, **self.flow_params_serializer.data)

    def execute(self, document_list, knowledge_id, split_strategy, paragraph_title_relate_problem_type,
                paragraph_title_relate_problem, paragraph_title_relate_problem_reference,
                document_name_relate_problem_type, document_name_relate_problem,
                document_name_relate_problem_reference, limit, limit_type, limit_reference, chunk_size, chunk_size_type,
                chunk_size_reference, patterns, patterns_type, patterns_reference, with_filter, with_filter_type,
                with_filter_reference, **kwargs) -> NodeResult:
        pass
