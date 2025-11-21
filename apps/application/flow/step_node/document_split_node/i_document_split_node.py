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
    patterns = serializers.ListField(
        required=False, label=_("patterns"), child=serializers.CharField(), default=[]
    )
    with_filter = serializers.BooleanField(
        required=False, label=_("with filter"), default=False
    )


class IDocumentSplitNode(INode):
    type = 'document-split-node'
    support = [
        WorkflowMode.APPLICATION, WorkflowMode.APPLICATION_LOOP, WorkflowMode.KNOWLEDGE_LOOP, WorkflowMode.KNOWLEDGE
    ]

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return DocumentSplitNodeSerializer

    def _run(self):
        # res = self.workflow_manage.get_reference_field(self.node_params_serializer.data.get('file_list')[0],
        #                                                self.node_params_serializer.data.get('file_list')[1:])
        return self.execute(**self.node_params_serializer.data, **self.flow_params_serializer.data)

    def execute(self, document_list, knowledge_id, split_strategy, paragraph_title_relate_problem_type,
                paragraph_title_relate_problem, paragraph_title_relate_problem_reference,
                document_name_relate_problem_type, document_name_relate_problem,
                document_name_relate_problem_reference, limit, patterns, with_filter, **kwargs) -> NodeResult:
        pass
