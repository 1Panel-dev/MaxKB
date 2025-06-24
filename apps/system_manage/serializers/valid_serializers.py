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
from django.core.cache import cache
from django.db.models import QuerySet
from rest_framework import serializers

from application.models import Application
from common.constants.cache_version import Cache_Version
from common.exception.app_exception import AppApiException
from knowledge.models import Knowledge
from users.models import User
from django.utils.translation import gettext_lazy as _

model_message_dict = {
    'dataset': {'model': Knowledge, 'count': 50,
                'message': _(
                    'The community version supports up to 50 knowledge bases. If you need more knowledge bases, please contact us (https://fit2cloud.com/).')},
    'application': {'model': Application, 'count': 5,
                    'message': _(
                        'The community version supports up to 5 applications. If you need more applications, please contact us (https://fit2cloud.com/).')},
    'user': {'model': User, 'count': 2,
             'message': _(
                 'The community version supports up to 2 users. If you need more users, please contact us (https://fit2cloud.com/).')}
}


class ValidSerializer(serializers.Serializer):
    valid_type = serializers.CharField(required=True, label=_('type'), validators=[
        validators.RegexValidator(regex=re.compile("^application|knowledge|user$"),
                                  message="类型只支持:application|knowledge|user", code=500)
    ])
    valid_count = serializers.IntegerField(required=True, label=_('check quantity'))

    def valid(self, is_valid=True):
        if is_valid:
            self.is_valid(raise_exception=True)
        model_value = model_message_dict.get(self.data.get('valid_type'))
        license_is_valid = cache.get(Cache_Version.SYSTEM.get_key(key='license_is_valid'),
                                     version=Cache_Version.SYSTEM.get_version())
        is_license_valid = license_is_valid if license_is_valid is not None else False
        if not is_license_valid:
            if self.data.get('valid_count') != model_value.get('count'):
                raise AppApiException(400, model_value.get('message'))
            if QuerySet(
                    model_value.get('model')).count() >= model_value.get('count'):
                raise AppApiException(400, model_value.get('message'))
        return True
