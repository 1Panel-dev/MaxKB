# coding=utf-8
"""
@project: MaxKB
@Author：虎虎
@file： api.py
@date：2025/4/14 15:20
@desc:
"""

import copy

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class DefaultResultSerializer(serializers.Serializer):
    """
    响应结果
    """

    code = serializers.IntegerField(required=True, help_text=_("response code"), label=_("response code"))
    message = serializers.CharField(
        required=False, default="success", help_text=_("error prompt"), label=_("error prompt")
    )
    data = serializers.BooleanField(required=False, default=True)


class ResultSerializer(serializers.Serializer):
    """
    响应结果
    """

    code = serializers.IntegerField(required=True, help_text=_("response code"), label=_("response code"))
    message = serializers.CharField(
        required=False, default="success", help_text=_("error prompt"), label=_("error prompt")
    )

    def get_data(self):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["data"] = self.get_data()


class PageDataResponse(serializers.Serializer):
    """
    分页数据
    """

    total = serializers.IntegerField(required=True, label=_("total number of data"))
    current = serializers.IntegerField(required=True, label=_("current page"))
    size = serializers.IntegerField(required=True, label=_("page size"))

    def __init__(self, records=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if records is not None:
            self._records_serializer = copy.deepcopy(records)
            self.fields["records"] = records


class ResultPageSerializer(ResultSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        records = self.get_data()
        if isinstance(records, PageDataResponse):
            records = records._records_serializer
        page_class = type(
            f"{self.__class__.__name__}PageData",
            (PageDataResponse,),
            {"__module__": PageDataResponse.__module__},
        )
        self.fields["data"] = page_class(records)
