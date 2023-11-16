# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： provider_serializers.py
    @date：2023/11/2 14:01
    @desc:
"""
import json
import uuid
from typing import Dict

from django.db.models import QuerySet
from rest_framework import serializers

from common.exception.app_exception import AppApiException
from common.util.rsa_util import encrypt, decrypt
from setting.models.model_management import Model
from setting.models_provider.constants.model_provider_constants import ModelProvideConstants


class ModelSerializer(serializers.Serializer):
    class Query(serializers.Serializer):
        user_id = serializers.UUIDField(required=True)

        name = serializers.CharField(required=False)

        model_type = serializers.CharField(required=False)

        model_name = serializers.CharField(required=False)

        def list(self, with_valid):
            if with_valid:
                self.is_valid(raise_exception=True)
            user_id = self.data.get('user_id')
            name = self.data.get('name')
            model_query_set = QuerySet(Model).filter(user_id=user_id)
            query_params = {}
            if name is not None:
                query_params['name__contains'] = name
            if self.data.get('model_type') is not None:
                query_params['model_type'] = self.data.get('model_type')
            if self.data.get('model_name') is not None:
                query_params['model_name'] = self.data.get('model_name')
            return [ModelSerializer.model_to_dict(model) for model in model_query_set.filter(**query_params)]

    class Create(serializers.Serializer):
        user_id = serializers.CharField(required=True)

        name = serializers.CharField(required=True)

        provider = serializers.CharField(required=True)

        model_type = serializers.CharField(required=True)

        model_name = serializers.CharField(required=True)

        credential = serializers.DictField(required=True)

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            if QuerySet(Model).filter(user_id=self.data.get('user_id'),
                                      name=self.data.get('name')).exists():
                raise AppApiException(500, f'模型名称【{self.data.get("name")}】已存在')
            # 校验模型认证数据
            ModelProvideConstants[self.data.get('provider')].value.get_model_credential(self.data.get('model_type'),
                                                                                        self.data.get(
                                                                                            'model_name')).is_valid(
                self.data.get('model_type'),
                self.data.get('model_name'),
                self.data.get('credential'),
                raise_exception=True)

        def insert(self, user_id, with_valid=False):
            if with_valid:
                self.is_valid(raise_exception=True)
            credential = self.data.get('credential')
            name = self.data.get('name')
            provider = self.data.get('provider')
            model_type = self.data.get('model_type')
            model_name = self.data.get('model_name')
            model_credential_str = json.dumps(credential)
            model = Model(id=uuid.uuid1(), user_id=user_id, name=name,
                          credential=encrypt(model_credential_str),
                          provider=provider, model_type=model_type, model_name=model_name)
            model.save()
            return ModelSerializer.Operate(data={'id': model.id}).one(user_id, with_valid=True)

    @staticmethod
    def model_to_dict(model: Model):
        credential = json.loads(decrypt(model.credential))
        return {'id': str(model.id), 'provider': model.provider, 'name': model.name, 'model_type': model.model_type,
                'model_name': model.model_name,
                'credential': ModelProvideConstants[model.provider].value.get_model_credential(model.model_type,
                                                                                               model.model_name).encryption_dict(
                    credential)}

    class Operate(serializers.Serializer):
        id = serializers.UUIDField(required=True)

        def one(self, user_id, with_valid=False):
            if with_valid:
                self.is_valid(raise_exception=True)
            model = QuerySet(Model).get(id=self.data.get('id'), user_id=user_id)
            return ModelSerializer.model_to_dict(model)


class ProviderSerializer(serializers.Serializer):
    provider = serializers.CharField(required=True)

    method = serializers.CharField(required=True)

    def exec(self, exec_params: Dict[str, object], with_valid=False):
        if with_valid:
            self.is_valid(raise_exception=True)

        provider = self.data.get('provider')
        method = self.data.get('method')
        return getattr(ModelProvideConstants[provider].value, method)(exec_params)
