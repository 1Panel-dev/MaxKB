# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： common_serializers.py
    @date：2023/11/17 11:00
    @desc:
"""
import os
from typing import List

from django.db.models import QuerySet
from drf_yasg import openapi
from rest_framework import serializers

from common.db.search import native_search
from common.db.sql_execute import update_execute
from common.exception.app_exception import AppApiException
from common.mixins.api_mixin import ApiMixin
from common.util.field_message import ErrMessage
from common.util.file_util import get_file_content
from common.util.fork import Fork
from dataset.models import Paragraph
from smartdoc.conf import PROJECT_DIR


def update_document_char_length(document_id: str):
    update_execute(get_file_content(
        os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'update_document_char_length.sql')),
        (document_id, document_id))


def list_paragraph(paragraph_list: List[str]):
    if paragraph_list is None or len(paragraph_list) == 0:
        return []
    return native_search(QuerySet(Paragraph).filter(id__in=paragraph_list), get_file_content(
        os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'list_paragraph.sql')))


class MetaSerializer(serializers.Serializer):
    class WebMeta(serializers.Serializer):
        source_url = serializers.CharField(required=True, error_messages=ErrMessage.char("文档地址"))
        selector = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                         error_messages=ErrMessage.char("选择器"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            source_url = self.data.get('source_url')
            response = Fork(source_url, []).fork()
            if response.status == 500:
                raise AppApiException(500, f"url错误,无法解析【{source_url}】")

    class BaseMeta(serializers.Serializer):
        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)


class BatchSerializer(ApiMixin, serializers.Serializer):
    id_list = serializers.ListField(required=True, child=serializers.UUIDField(required=True),
                                    error_messages=ErrMessage.char("id列表"))

    def is_valid(self, *, model=None, raise_exception=False):
        super().is_valid(raise_exception=True)
        if model is not None:
            id_list = self.data.get('id_list')
            model_list = QuerySet(model).filter(id__in=id_list)
            if len(model_list) != len(id_list):
                model_id_list = [str(m.id) for m in model_list]
                error_id_list = list(filter(lambda row_id: not model_id_list.__contains__(row_id), id_list))
                raise AppApiException(500, f"id不正确:{error_id_list}")

    @staticmethod
    def get_request_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id_list': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING),
                                          title="主键id列表",
                                          description="主键id列表")
            }
        )
