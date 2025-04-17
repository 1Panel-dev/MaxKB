# -*- coding: utf-8 -*-
import json
import threading
import time
from typing import Dict

import uuid_utils.compat as uuid
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.exception.app_exception import AppApiException
from common.utils.rsa_util import rsa_long_encrypt, rsa_long_decrypt
from models_provider.base_model_provider import ValidCode, DownModelChunkStatus
from models_provider.constants.model_provider_constants import ModelProvideConstants
from models_provider.models import Model, Status


class ModelModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = [
            'id', 'name', 'status', 'model_type', 'model_name',
            'user', 'provider', 'credential', 'meta',
            'model_params_form', 'workspace_id'
        ]


class ModelCreateRequest(serializers.Serializer):
    name = serializers.CharField(required=True, max_length=64, label=_("model name"))
    provider = serializers.CharField(required=True, label=_("provider"))
    model_type = serializers.CharField(required=True, label=_("model type"))
    model_name = serializers.CharField(required=True, label=_("model name"))
    model_params_form = serializers.ListField(required=False, default=list, label=_("parameter configuration"))
    credential = serializers.DictField(required=True, label=_("certification information"))


class ModelPullManage:
    @staticmethod
    def pull(model: Model, credential: Dict):
        try:
            response = ModelProvideConstants[model.provider].value.down_model(
                model.model_type, model.model_name, credential
            )
            down_model_chunk = {}
            last_update_time = time.time()

            for chunk in response:
                down_model_chunk[chunk.digest] = chunk.to_dict()
                if time.time() - last_update_time > 5:
                    current_model = QuerySet(Model).filter(id=model.id).first()
                    if current_model and current_model.status == Status.PAUSE_DOWNLOAD:
                        return
                    QuerySet(Model).filter(id=model.id).update(
                        meta={"down_model_chunk": list(down_model_chunk.values())}
                    )
                    last_update_time = time.time()

            status = Status.ERROR
            message = ""
            for chunk in down_model_chunk.values():
                if chunk.get('status') == DownModelChunkStatus.success.value:
                    status = Status.SUCCESS
                elif chunk.get('status') == DownModelChunkStatus.error.value:
                    message = chunk.get("digest")

            QuerySet(Model).filter(id=model.id).update(
                meta={"down_model_chunk": [], "message": message},
                status=status
            )
        except Exception as e:
            QuerySet(Model).filter(id=model.id).update(
                meta={"down_model_chunk": [], "message": str(e)},
                status=Status.ERROR
            )


class ModelSerializer(serializers.Serializer):
    @staticmethod
    def model_to_dict(model: Model):
        credential = json.loads(rsa_long_decrypt(model.credential))
        return {
            'id': str(model.id),
            'provider': model.provider,
            'name': model.name,
            'model_type': model.model_type,
            'model_name': model.model_name,
            'status': model.status,
            'meta': model.meta,
            'credential': ModelProvideConstants[model.provider].value.get_model_credential(
                model.model_type, model.model_name
            ).encryption_dict(credential),
            'workspace_id': model.workspace_id
        }

    class Operate(serializers.Serializer):
        id = serializers.UUIDField(required=True, label=_("模型id"))
        user_id = serializers.UUIDField(required=True, label=_("user id"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            model = QuerySet(Model).filter(
                id=self.data.get("id"), user_id=self.data.get("user_id")
            ).first()
            if model is None:
                raise AppApiException(500, _('模型不存在'))

        def one(self, with_valid=False):
            if with_valid:
                self.is_valid(raise_exception=True)
            model = QuerySet(Model).get(
                id=self.data.get('id'), user_id=self.data.get('user_id')
            )
            return ModelSerializer.model_to_dict(model)

    class Create(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, label=_('user id'))
        name = serializers.CharField(required=True, max_length=64, label=_("model name"))
        provider = serializers.CharField(required=True, label=_("provider"))
        model_type = serializers.CharField(required=True, label=_("model type"))
        model_name = serializers.CharField(required=True, label=_("model name"))
        model_params_form = serializers.ListField(required=False, default=list, label=_("parameter configuration"))
        credential = serializers.DictField(required=True, label=_("certification information"))
        workspace_id = serializers.CharField(required=False, label=_("workspace id"), max_length=128)

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            if QuerySet(Model).filter(
                    user_id=self.data.get('user_id'),
                    name=self.data.get('name'),
                    workspace_id=self.data.get('workspace_id')
            ).exists():
                raise AppApiException(
                    500,
                    _('Model name【{model_name}】already exists').format(model_name=self.data.get("name"))
                )
            default_params = {item['field']: item['default_value'] for item in self.data.get('model_params_form')}
            ModelProvideConstants[self.data.get('provider')].value.is_valid_credential(
                self.data.get('model_type'),
                self.data.get('model_name'),
                self.data.get('credential'),
                default_params,
                raise_exception=True
            )

        def insert(self, workspace_id, with_valid=True):
            status = Status.SUCCESS
            if with_valid:
                try:
                    self.is_valid(raise_exception=True)
                except AppApiException as e:
                    if e.code == ValidCode.model_not_fount:
                        status = Status.DOWNLOAD
                    else:
                        raise e

            credential = self.data.get('credential')
            model_data = {
                'id': uuid.uuid1(),
                'status': status,
                'user_id': self.data.get('user_id'),
                'name': self.data.get('name'),
                'credential': rsa_long_encrypt(json.dumps(credential)),
                'provider': self.data.get('provider'),
                'model_type': self.data.get('model_type'),
                'model_name': self.data.get('model_name'),
                'model_params_form': self.data.get('model_params_form'),
                'workspace_id': workspace_id
            }
            model = Model(**model_data)
            try:
                model.save()
            except Exception as save_error:
                # 可添加日志记录
                raise AppApiException(500, _('模型保存失败')) from save_error

            if status == Status.DOWNLOAD:
                thread = threading.Thread(target=ModelPullManage.pull, args=(model, credential))
                thread.start()

            return ModelModelSerializer(model).data
