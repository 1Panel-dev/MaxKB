# coding=utf-8

from application.flow.step_node.document_extract_node.i_document_extract_node import IDocumentExtractNode


class BaseDocumentExtractNode(IDocumentExtractNode):
    def execute(self, file_list, **kwargs):
        pass

    def get_details(self, index: int, **kwargs):
        pass
