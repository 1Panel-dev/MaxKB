# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： I_base_chat_pipeline.py
    @date：2024/1/9 17:25
    @desc:
"""
import time
from abc import abstractmethod
from typing import Type

from rest_framework import serializers

from knowledge.models import Paragraph


class ParagraphPipelineModel:

    def __init__(self, _id: str, document_id: str, knowledge_id: str, content: str, title: str, status: str,
                 is_active: bool, comprehensive_score: float, similarity: float, knowledge_name: str,
                 document_name: str,
                 hit_handling_method: str, directly_return_similarity: float, knowledge_type, meta: dict = None):
        self.id = _id
        self.document_id = document_id
        self.knowledge_id = knowledge_id
        self.content = content
        self.title = title
        self.status = status,
        self.is_active = is_active
        self.comprehensive_score = comprehensive_score
        self.similarity = similarity
        self.knowledge_name = knowledge_name
        self.document_name = document_name
        self.hit_handling_method = hit_handling_method
        self.directly_return_similarity = directly_return_similarity
        self.meta = meta
        self.knowledge_type = knowledge_type

    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'knowledge_id': self.knowledge_id,
            'content': self.content,
            'title': self.title,
            'status': self.status,
            'is_active': self.is_active,
            'comprehensive_score': self.comprehensive_score,
            'similarity': self.similarity,
            'knowledge_name': self.knowledge_name,
            'document_name': self.document_name,
            'knowledge_type': self.knowledge_type,
            'meta': self.meta,
        }

    class builder:
        def __init__(self):
            self.similarity = None
            self.paragraph = {}
            self.comprehensive_score = None
            self.document_name = None
            self.knowledge_name = None
            self.knowledge_type = None
            self.hit_handling_method = None
            self.directly_return_similarity = 0.9
            self.meta = {}

        def add_paragraph(self, paragraph):
            if isinstance(paragraph, Paragraph):
                self.paragraph = {'id': paragraph.id,
                                  'document_id': paragraph.document_id,
                                  'knowledge_id': paragraph.knowledge_id,
                                  'content': paragraph.content,
                                  'title': paragraph.title,
                                  'status': paragraph.status,
                                  'is_active': paragraph.is_active,
                                  }
            else:
                self.paragraph = paragraph
            return self

        def add_knowledge_name(self, knowledge_name):
            self.knowledge_name = knowledge_name
            return self

        def add_knowledge_type(self, knowledge_type):
            self.knowledge_type = knowledge_type
            return self

        def add_document_name(self, document_name):
            self.document_name = document_name
            return self

        def add_hit_handling_method(self, hit_handling_method):
            self.hit_handling_method = hit_handling_method
            return self

        def add_directly_return_similarity(self, directly_return_similarity):
            self.directly_return_similarity = directly_return_similarity
            return self

        def add_comprehensive_score(self, comprehensive_score: float):
            self.comprehensive_score = comprehensive_score
            return self

        def add_similarity(self, similarity: float):
            self.similarity = similarity
            return self

        def add_meta(self, meta: dict):
            self.meta = meta
            return self

        def build(self):
            return ParagraphPipelineModel(str(self.paragraph.get('id')), str(self.paragraph.get('document_id')),
                                          str(self.paragraph.get('knowledge_id')),
                                          self.paragraph.get('content'), self.paragraph.get('title'),
                                          self.paragraph.get('status'),
                                          self.paragraph.get('is_active'),
                                          self.comprehensive_score, self.similarity, self.knowledge_name,
                                          self.document_name, self.hit_handling_method, self.directly_return_similarity,
                                          self.knowledge_type,
                                          self.meta)


class IBaseChatPipelineStep:
    def __init__(self):
        # 当前步骤上下文,用于存储当前步骤信息
        self.context = {}

    @abstractmethod
    def get_step_serializer(self, manage) -> Type[serializers.Serializer]:
        pass

    def valid_args(self, manage):
        step_serializer_clazz = self.get_step_serializer(manage)
        step_serializer = step_serializer_clazz(data=manage.context)
        step_serializer.is_valid(raise_exception=True)
        self.context['step_args'] = step_serializer.data

    def run(self, manage):
        """

        :param manage:      步骤管理器
        :return: 执行结果
        """
        start_time = time.time()
        self.context['start_time'] = start_time
        # 校验参数,
        self.valid_args(manage)
        self._run(manage)
        self.context['run_time'] = time.time() - start_time

    def _run(self, manage):
        pass

    def execute(self, **kwargs):
        pass

    def get_details(self, manage, **kwargs):
        """
        运行详情
        :return: 步骤详情
        """
        return None
