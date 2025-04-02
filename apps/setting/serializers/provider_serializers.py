# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： provider_serializers.py
    @date：2023/11/2 14:01
    @desc:
"""
import json
import re
import threading
import time
import uuid
from typing import Dict

from django.core import validators
from django.db.models import QuerySet, Q
from rest_framework import serializers

from application.models import Application
from common.config.embedding_config import ModelManage
from common.exception.app_exception import AppApiException
from common.util.field_message import ErrMessage
from common.util.rsa_util import rsa_long_decrypt, rsa_long_encrypt
from dataset.models import DataSet
from setting.models.model_management import Model, Status, PermissionType
from setting.models_provider import get_model, get_model_credential
from setting.models_provider.base_model_provider import ValidCode, DownModelChunkStatus
from setting.models_provider.constants.model_provider_constants import ModelProvideConstants
from django.utils.translation import gettext_lazy as _


def get_default_model_params_setting(provider, model_type, model_name):
    credential = get_model_credential(provider, model_type, model_name)
    setting_form = credential.get_model_params_setting_form(model_name)
    if setting_form is not None:
        return setting_form.to_form_list()
    return []


class ModelPullManage:

    @staticmethod
    def pull(model: Model, credential: Dict):
        try:
            response = ModelProvideConstants[model.provider].value.down_model(model.model_type, model.model_name,
                                                                              credential)
            down_model_chunk = {}
            timestamp = time.time()
            for chunk in response:
                down_model_chunk[chunk.digest] = chunk.to_dict()
                if time.time() - timestamp > 5:
                    model_new = QuerySet(Model).filter(id=model.id).first()
                    if model_new.status == Status.PAUSE_DOWNLOAD:
                        return
                    QuerySet(Model).filter(id=model.id).update(
                        meta={"down_model_chunk": list(down_model_chunk.values())})
                    timestamp = time.time()
            status = Status.ERROR
            message = ""
            down_model_chunk_list = list(down_model_chunk.values())
            for chunk in down_model_chunk_list:
                if chunk.get('status') == DownModelChunkStatus.success.value:
                    status = Status.SUCCESS
                if chunk.get('status') == DownModelChunkStatus.error.value:
                    message = chunk.get("digest")
            QuerySet(Model).filter(id=model.id).update(meta={"down_model_chunk": [], "message": message},
                                                       status=status)
        except Exception as e:
            QuerySet(Model).filter(id=model.id).update(meta={"down_model_chunk": [], "message": str(e)},
                                                       status=Status.ERROR)


class ModelSerializer(serializers.Serializer):
    class Query(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_('user id')))

        name = serializers.CharField(required=False, max_length=64,
                                     error_messages=ErrMessage.char(_('model name')))

        model_type = serializers.CharField(required=False, error_messages=ErrMessage.char(_('model type')))

        model_name = serializers.CharField(required=False, error_messages=ErrMessage.char(_('model name')))

        provider = serializers.CharField(required=False, error_messages=ErrMessage.char(_('provider')))

        permission_type = serializers.CharField(required=False, error_messages=ErrMessage.char(_('permission type')))

        create_user = serializers.CharField(required=False, error_messages=ErrMessage.char(_('create user')))

        def list(self, with_valid):
            if with_valid:
                self.is_valid(raise_exception=True)
            user_id = self.data.get('user_id')
            name = self.data.get('name')
            create_user = self.data.get('create_user')
            if create_user is not None:
                # 当前用户能查看自己的模型，包括公开和私有的
                if create_user == user_id:
                    model_query_set = QuerySet(Model).filter(Q(user_id=create_user))
                # 当前用户能查看其他人的模型，只能查看公开的
                else:
                    model_query_set = QuerySet(Model).filter(
                        (Q(user_id=self.data.get('create_user')) & Q(permission_type='PUBLIC')))
            else:
                model_query_set = QuerySet(Model).filter((Q(user_id=user_id) | Q(permission_type='PUBLIC')))
            query_params = {}
            if name is not None:
                query_params['name__icontains'] = name
            if self.data.get('model_type') is not None:
                query_params['model_type'] = self.data.get('model_type')
            if self.data.get('model_name') is not None:
                query_params['model_name'] = self.data.get('model_name')
            if self.data.get('provider') is not None:
                query_params['provider'] = self.data.get('provider')
            if self.data.get('permission_type') is not None:
                query_params['permission_type'] = self.data.get('permission_type')

            return [
                {'id': str(model.id), 'provider': model.provider, 'name': model.name, 'model_type': model.model_type,
                 'model_name': model.model_name, 'status': model.status, 'meta': model.meta,
                 'permission_type': model.permission_type, 'user_id': model.user_id, 'username': model.user.username}
                for model in
                model_query_set.filter(**query_params).order_by("-create_time")]

    class Edit(serializers.Serializer):
        user_id = serializers.CharField(required=False, error_messages=ErrMessage.uuid(_('user id')))

        name = serializers.CharField(required=False, max_length=64,
                                     error_messages=ErrMessage.char(_("model name")))

        model_type = serializers.CharField(required=False, error_messages=ErrMessage.char(_("model type")))

        permission_type = serializers.CharField(required=False, error_messages=ErrMessage.char(_("permission type")),
                                                validators=[
                                                    validators.RegexValidator(regex=re.compile("^PUBLIC|PRIVATE$"),
                                                                              message=_(
                                                                                  "permissions only supportPUBLIC|PRIVATE"),
                                                                              code=500)
                                                ])

        model_name = serializers.CharField(required=False, error_messages=ErrMessage.char(_("model type")))

        credential = serializers.DictField(required=False,
                                           error_messages=ErrMessage.dict(_("certification information")))

        def is_valid(self, model=None, raise_exception=False):
            super().is_valid(raise_exception=True)
            filter_params = {'user_id': self.data.get('user_id')}
            if 'name' in self.data and self.data.get('name') is not None:
                filter_params['name'] = self.data.get('name')
                if QuerySet(Model).exclude(id=model.id).filter(**filter_params).exists():
                    raise AppApiException(500, f'模型名称【{self.data.get("name")}】已存在')

            ModelSerializer.model_to_dict(model)

            provider = model.provider
            model_type = self.data.get('model_type')
            model_name = self.data.get(
                'model_name')
            credential = self.data.get('credential')
            provider_handler = ModelProvideConstants[provider].value
            model_credential = ModelProvideConstants[provider].value.get_model_credential(model_type,
                                                                                          model_name)
            source_model_credential = json.loads(rsa_long_decrypt(model.credential))
            source_encryption_model_credential = model_credential.encryption_dict(source_model_credential)
            if credential is not None:
                for k in source_encryption_model_credential.keys():
                    if k in credential and credential[k] == source_encryption_model_credential[k]:
                        credential[k] = source_model_credential[k]
            return credential, model_credential, provider_handler

    class Create(serializers.Serializer):
        user_id = serializers.CharField(required=True, error_messages=ErrMessage.uuid(_("user id")))

        name = serializers.CharField(required=True, max_length=64, error_messages=ErrMessage.char(_("model name")))

        provider = serializers.CharField(required=True, error_messages=ErrMessage.char(_("provider")))

        model_type = serializers.CharField(required=True, error_messages=ErrMessage.char(_("model type")))

        permission_type = serializers.CharField(required=True, error_messages=ErrMessage.char(_("permission type")),
                                                validators=[
                                                    validators.RegexValidator(regex=re.compile("^PUBLIC|PRIVATE$"),
                                                                              message=_(
                                                                                  "permissions only supportPUBLIC|PRIVATE"),
                                                                              code=500)
                                                ])

        model_name = serializers.CharField(required=True, error_messages=ErrMessage.char(_("model name")))

        model_params_form = serializers.ListField(required=False, default=list,
                                                  error_messages=ErrMessage.char(_("parameter configuration")))

        credential = serializers.DictField(required=True,
                                           error_messages=ErrMessage.dict(_("certification information")))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            if QuerySet(Model).filter(user_id=self.data.get('user_id'),
                                      name=self.data.get('name')).exists():
                raise AppApiException(500, _('Model name【{model_name}】already exists').format(
                    model_name=self.data.get("name")))
            default_params = {item['field']: item['default_value'] for item in self.data.get('model_params_form')}
            ModelProvideConstants[self.data.get('provider')].value.is_valid_credential(self.data.get('model_type'),
                                                                                       self.data.get('model_name'),
                                                                                       self.data.get('credential'),
                                                                                       default_params,
                                                                                       raise_exception=True
                                                                                       )

        def insert(self, user_id, with_valid=False):
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
            name = self.data.get('name')
            provider = self.data.get('provider')
            model_type = self.data.get('model_type')
            model_name = self.data.get('model_name')
            permission_type = self.data.get('permission_type')
            model_params_form = self.data.get('model_params_form')
            model_credential_str = json.dumps(credential)
            model = Model(id=uuid.uuid1(), status=status, user_id=user_id, name=name,
                          credential=rsa_long_encrypt(model_credential_str),
                          provider=provider, model_type=model_type, model_name=model_name,
                          model_params_form=model_params_form,
                          permission_type=permission_type)
            model.save()
            if status == Status.DOWNLOAD:
                thread = threading.Thread(target=ModelPullManage.pull, args=(model, credential))
                thread.start()
            return ModelSerializer.Operate(data={'id': model.id, 'user_id': user_id}).one(with_valid=True)

    @staticmethod
    def model_to_dict(model: Model):
        credential = json.loads(rsa_long_decrypt(model.credential))
        return {'id': str(model.id), 'provider': model.provider, 'name': model.name, 'model_type': model.model_type,
                'model_name': model.model_name,
                'status': model.status,
                'meta': model.meta,
                'credential': ModelProvideConstants[model.provider].value.get_model_credential(model.model_type,
                                                                                               model.model_name).encryption_dict(
                    credential),
                'permission_type': model.permission_type}

    class ModelParams(serializers.Serializer):
        id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("模型id"))

        user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_("user id")))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            model = QuerySet(Model).filter(id=self.data.get("id")).first()
            if model is None:
                raise AppApiException(500, '模型不存在')
            if model.permission_type == PermissionType.PRIVATE and self.data.get('user_id') != str(model.user_id):
                raise AppApiException(500, '没有权限访问到此模型')

        def get_model_params(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            model_id = self.data.get('id')
            model = QuerySet(Model).filter(id=model_id).first()
            # 已经保存过的模型参数表单
            return model.model_params_form

    class ModelParamsForm(serializers.Serializer):
        id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("模型id"))

        user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_("user id")))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            model = QuerySet(Model).filter(id=self.data.get("id")).first()
            if model is None:
                raise AppApiException(500, '模型不存在')
            if model.permission_type == PermissionType.PRIVATE and self.data.get('user_id') != str(model.user_id):
                raise AppApiException(500, '没有权限访问到此模型')

        def save_model_params_form(self, model_params_form, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            if model_params_form is None:
                model_params_form = []
            model_id = self.data.get('id')
            model = QuerySet(Model).filter(id=model_id).first()
            model.model_params_form = model_params_form
            model.save()
            return True

    class Operate(serializers.Serializer):
        id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("模型id"))

        user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_("user id")))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            model = QuerySet(Model).filter(id=self.data.get("id"), user_id=self.data.get("user_id")).first()
            if model is None:
                raise AppApiException(500, '模型不存在')

        def one(self, with_valid=False):
            if with_valid:
                self.is_valid(raise_exception=True)
            model = QuerySet(Model).get(id=self.data.get('id'), user_id=self.data.get('user_id'))
            return ModelSerializer.model_to_dict(model)

        def one_meta(self, with_valid=False):
            model = None
            if with_valid:
                super().is_valid(raise_exception=True)
                model = QuerySet(Model).filter(id=self.data.get("id")).first()
                if model is None:
                    raise AppApiException(500, _('Model does not exist'))
                if model.permission_type == 'PRIVATE' and str(model.user_id) != str(self.data.get("user_id")):
                    raise Exception(_('No permission to use this model') + f"{model.name}")
            if model is None:
                model = QuerySet(Model).get(id=self.data.get('id'))
            return {'id': str(model.id), 'provider': model.provider, 'name': model.name, 'model_type': model.model_type,
                    'model_name': model.model_name,
                    'status': model.status,
                    'meta': model.meta
                    }

        def delete(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            model_id = self.data.get('id')
            model = Model.objects.filter(id=model_id).first()
            if not model:
                # 模型不存在，直接返回或抛出异常
                raise AppApiException(500, "模型不存在")
            if model.model_type == 'LLM':
                application_count = Application.objects.filter(model_id=model_id).count()
                if application_count > 0:
                    raise AppApiException(500, f"该模型关联了{application_count} 个应用，无法删除该模型。")
            elif model.model_type == 'EMBEDDING':
                dataset_count = DataSet.objects.filter(embedding_mode_id=model_id).count()
                if dataset_count > 0:
                    raise AppApiException(500, f"该模型关联了{dataset_count} 个知识库，无法删除该模型。")
            elif model.model_type == 'TTS':
                dataset_count = Application.objects.filter(tts_model_id=model_id).count()
                if dataset_count > 0:
                    raise AppApiException(500, f"该模型关联了{dataset_count} 个应用，无法删除该模型。")
            elif model.model_type == 'STT':
                dataset_count = Application.objects.filter(stt_model_id=model_id).count()
                if dataset_count > 0:
                    raise AppApiException(500, f"该模型关联了{dataset_count} 个应用，无法删除该模型。")
            model.delete()
            return True

        def pause_download(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            QuerySet(Model).filter(id=self.data.get('id')).update(status=Status.PAUSE_DOWNLOAD)
            return True

        def edit(self, instance: Dict, user_id: str, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            model = QuerySet(Model).filter(id=self.data.get('id')).first()

            if model is None:
                raise AppApiException(500, '不存在的id')
            else:
                credential, model_credential, provider_handler = ModelSerializer.Edit(
                    data={**instance, 'user_id': user_id}).is_valid(
                    model=model)
                try:
                    model.status = Status.SUCCESS
                    default_params = {item['field']: item['default_value'] for item in model.model_params_form}
                    # 校验模型认证数据
                    provider_handler.is_valid_credential(model.model_type,
                                                         instance.get("model_name"),
                                                         credential,
                                                         default_params,
                                                         raise_exception=True)

                except AppApiException as e:
                    if e.code == ValidCode.model_not_fount:
                        model.status = Status.DOWNLOAD
                    else:
                        raise e
                update_keys = ['credential', 'name', 'model_type', 'model_name', 'permission_type']
                for update_key in update_keys:
                    if update_key in instance and instance.get(update_key) is not None:
                        if update_key == 'credential':
                            model_credential_str = json.dumps(credential)
                            model.__setattr__(update_key, rsa_long_encrypt(model_credential_str))
                        else:
                            model.__setattr__(update_key, instance.get(update_key))
            # 修改模型时候删除缓存
            ModelManage.delete_key(str(model.id))
            model.save()
            if model.status == Status.DOWNLOAD:
                thread = threading.Thread(target=ModelPullManage.pull, args=(model, credential))
                thread.start()
            return self.one(with_valid=False)


class ProviderSerializer(serializers.Serializer):
    provider = serializers.CharField(required=True, error_messages=ErrMessage.char(_("provider")))

    method = serializers.CharField(required=True, error_messages=ErrMessage.char("执行函数名称"))

    def exec(self, exec_params: Dict[str, object], with_valid=False):
        if with_valid:
            self.is_valid(raise_exception=True)

        provider = self.data.get('provider')
        method = self.data.get('method')
        return getattr(ModelProvideConstants[provider].value, method)(exec_params)
