# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： valid_serializers.py
    @date：2024/7/8 18:00
    @desc:
"""
import re

from django.core import validators
from django.db.models import QuerySet
from rest_framework import serializers

from application.models import Application
from common.exception.app_exception import AppApiException
from common.models.db_model_manage import DBModelManage
from common.util.field_message import ErrMessage
from dataset.models import DataSet
from users.models import User

model_message_dict = {
    'dataset': {'model': DataSet, 'count': 50,
                'message': '社区版最多支持 50 个知识库，如需拥有更多知识库，请联系我们（https://fit2cloud.com/）。'},
    'application': {'model': Application, 'count': 5,
                    'message': '社区版最多支持 5 个应用，如需拥有更多应用，请联系我们（https://fit2cloud.com/）。'},
    'user': {'model': User, 'count': 2,
             'message': '社区版最多支持 2 个用户，如需拥有更多用户，请联系我们（https://fit2cloud.com/）。'}
}


class ValidSerializer(serializers.Serializer):
    valid_type = serializers.CharField(required=True, error_messages=ErrMessage.char("类型"), validators=[
        validators.RegexValidator(regex=re.compile("^application|dataset|user$"),
                                  message="类型只支持:application|dataset|user", code=500)
    ])
    valid_count = serializers.IntegerField(required=True, error_messages=ErrMessage.integer("校验数量"))

    def valid(self, is_valid=True):
        if is_valid:
            self.is_valid(raise_exception=True)
        model_value = model_message_dict.get(self.data.get('valid_type'))
        xpack_cache = DBModelManage.get_model('xpack_cache')
        is_license_valid = xpack_cache.get('XPACK_LICENSE_IS_VALID', False) if xpack_cache is not None else False
        if not is_license_valid:
            if self.data.get('valid_count') != model_value.get('count'):
                raise AppApiException(400, model_value.get('message'))
            if QuerySet(
                    model_value.get('model')).count() >= model_value.get('count'):
                raise AppApiException(400, model_value.get('message'))
        return True
