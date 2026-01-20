# -*- coding: utf-8 -*-
import json
import os
import threading
import time
from typing import Dict

import uuid_utils.compat as uuid
from django.core.cache import cache
from django.db import transaction
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.config.embedding_config import ModelManage
from common.constants.cache_version import Cache_Version
from common.constants.permission_constants import ResourcePermission, ResourceAuthType
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.db.search import native_search
from common.exception.app_exception import AppApiException
from common.utils.common import get_file_content
from common.utils.rsa_util import rsa_long_encrypt, rsa_long_decrypt
from maxkb.conf import PROJECT_DIR
from models_provider.base_model_provider import ValidCode, DownModelChunkStatus
from models_provider.constants.model_provider_constants import ModelProvideConstants
from models_provider.models import Model, Status
from models_provider.tools import get_model_credential
from system_manage.models import WorkspaceUserResourcePermission, AuthTargetType
from system_manage.models.resource_mapping import ResourceMapping
from system_manage.serializers.resource_mapping_serializers import ResourceMappingSerializer
from system_manage.serializers.user_resource_permission import UserResourcePermissionSerializer
from users.serializers.user import is_workspace_manage


def get_default_model_params_setting(provider, model_type, model_name):
    credential = get_model_credential(provider, model_type, model_name)
    setting_form = credential.get_model_params_setting_form(model_name)
    if setting_form is not None:
        return setting_form.to_form_list()
    return []


class ModelModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = [
            'id', 'name', 'status', 'model_type', 'model_name',
            'user', 'provider', 'credential', 'meta',
            'model_params_form', 'workspace_id', 'create_time', 'update_time'
        ]


class ModelCreateRequest(serializers.Serializer):
    name = serializers.CharField(required=True, max_length=64, label=_("model name"))
    provider = serializers.CharField(required=True, label=_("provider"))
    model_type = serializers.CharField(required=True, label=_("model type"))
    model_name = serializers.CharField(required=True, label=_("base model"))
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
            'workspace_id': model.workspace_id,
            'nick_name': model.user.nick_name if model.user else '',
            'username': model.user.username if model.user else ''
        }

    class Operate(serializers.Serializer):
        id = serializers.UUIDField(required=True, label=_("model id"))
        user_id = serializers.UUIDField(required=False, label=_("user id"))
        workspace_id = serializers.CharField(required=False, label=_("workspace id"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            workspace_id = self.data.get("workspace_id")
            model_query = QuerySet(Model).filter(id=self.data.get("id"))
            if workspace_id is not None:
                model_query = model_query.filter(workspace_id=workspace_id)
            model = model_query.first()
            if model is None:
                raise AppApiException(500, _('Model does not exist'))
            if model.workspace_id == 'None':
                raise AppApiException(500, _('Shared models cannot be deleted or modified'))

        def one(self, with_valid=False):
            if with_valid:
                super().is_valid(raise_exception=True)
            model = QuerySet(Model).get(
                id=self.data.get('id'), workspace_id=self.data.get('workspace_id', 'None')
            )
            return ModelSerializer.model_to_dict(model)

        def one_meta(self, with_valid=False):
            model = None
            if with_valid:
                super().is_valid(raise_exception=True)
                model = QuerySet(Model).filter(id=self.data.get("id"),
                                               workspace_id=self.data.get('workspace_id', 'None')).first()
                if model is None:
                    raise AppApiException(500, _('Model does not exist'))
            return {'id': str(model.id), 'provider': model.provider, 'name': model.name, 'model_type': model.model_type,
                    'model_name': model.model_name,
                    'status': model.status,
                    'meta': model.meta,
                    'workspace_id': model.workspace_id,
                    }

        def pause_download(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            QuerySet(Model).filter(id=self.data.get('id')).update(status=Status.PAUSE_DOWNLOAD)
            return True

        @transaction.atomic
        def delete(self, with_valid=True):
            if with_valid:
                super().is_valid(raise_exception=True)
            model_id = self.data.get('id')
            model = Model.objects.filter(id=model_id).first()
            if model is None:
                return True
            QuerySet(WorkspaceUserResourcePermission).filter(target=model_id).delete()
            # TODO : 这里可以添加模型删除的逻辑,需要注意删除模型时的权限和关联关系
            # if model.model_type == 'LLM':
            #     application_count = Application.objects.filter(model_id=model_id).count()
            #     if application_count > 0:
            #         raise AppApiException(500, f"该模型关联了{application_count} 个应用，无法删除该模型。")
            # elif model.model_type == 'EMBEDDING':
            #     dataset_count = DataSet.objects.filter(embedding_model_id=model_id).count()
            #     if dataset_count > 0:
            #         raise AppApiException(500, f"该模型关联了{dataset_count} 个知识库，无法删除该模型。")
            # elif model.model_type == 'TTS':
            #     dataset_count = Application.objects.filter(tts_model_id=model_id).count()
            #     if dataset_count > 0:
            #         raise AppApiException(500, f"该模型关联了{dataset_count} 个应用，无法删除该模型。")
            # elif model.model_type == 'STT':
            #     dataset_count = Application.objects.filter(stt_model_id=model_id).count()
            #     if dataset_count > 0:
            #         raise AppApiException(500, f"该模型关联了{dataset_count} 个应用，无法删除该模型。")
            model.delete()
            ResourceMapping.objects.filter(target_id=model_id).delete()
            return True

        def edit(self, instance: Dict, user_id: str, with_valid=True):
            if with_valid:
                super().is_valid(raise_exception=True)
            model = QuerySet(Model).filter(id=self.data.get('id')).first()

            credential, model_credential, provider_handler = ModelSerializer.Edit(
                data={**instance}).is_valid(
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
            update_keys = ['credential', 'name', 'model_type', 'model_name']
            for update_key in update_keys:
                if update_key in instance and instance.get(update_key) is not None:
                    if update_key == 'credential':
                        model_credential_str = json.dumps(credential)
                        model.__setattr__(update_key, rsa_long_encrypt(model_credential_str))
                    else:
                        model.__setattr__(update_key, instance.get(update_key))

            ModelManage.delete_key(str(model.id))
            model.save()
            if model.status == Status.DOWNLOAD:
                thread = threading.Thread(target=ModelPullManage.pull, args=(model, credential))
                thread.start()
            return self.one(with_valid=False)

    class Edit(serializers.Serializer):
        user_id = serializers.CharField(required=False, label=(_('user id')))

        name = serializers.CharField(required=False, max_length=64,
                                     label=(_("model name")))

        model_type = serializers.CharField(required=False, label=(_("model type")))

        model_name = serializers.CharField(required=False, label=(_("base model")))

        credential = serializers.DictField(required=False,
                                           label=(_("certification information")))
        workspace_id = serializers.CharField(required=False, label=(_("workspace id")))

        def is_valid(self, model=None, raise_exception=False):
            super().is_valid(raise_exception=True)
            filter_params = {'workspace_id': model.workspace_id}
            if 'name' in self.data and self.data.get('name') is not None:
                filter_params['name'] = self.data.get('name')
                if QuerySet(Model).exclude(id=model.id).filter(**filter_params).exists():
                    raise AppApiException(500, _('base model【{model_name}】already exists').format(
                        model_name=self.data.get("name")))

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
        user_id = serializers.UUIDField(required=True, label=_('user id'))
        name = serializers.CharField(required=True, max_length=64, label=_("model name"))
        provider = serializers.CharField(required=True, label=_("provider"))
        model_type = serializers.CharField(required=True, label=_("model type"))
        model_name = serializers.CharField(required=True, label=_("base model"))
        model_params_form = serializers.ListField(required=False, default=list, label=_("parameter configuration"))
        credential = serializers.DictField(required=True, label=_("certification information"))
        workspace_id = serializers.CharField(required=False, label=_("workspace id"), max_length=128)

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            if QuerySet(Model).filter(
                    name=self.data.get('name'),
                    workspace_id=self.data.get('workspace_id', 'None')
            ).exists():
                raise AppApiException(
                    500,
                    _('base model【{model_name}】already exists').format(model_name=self.data.get("name"))
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
                'id': uuid.uuid7(),
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
                if workspace_id != 'None':
                    UserResourcePermissionSerializer(data={
                        'workspace_id': workspace_id,
                        'user_id': self.data.get('user_id'),
                        'auth_target_type': AuthTargetType.MODEL.value
                    }).auth_resource(str(model.id))
            except Exception as save_error:
                # 可添加日志记录
                raise AppApiException(500, _("Model saving failed")) from save_error

            if status == Status.DOWNLOAD:
                thread = threading.Thread(target=ModelPullManage.pull, args=(model, credential))
                thread.start()

            return ModelModelSerializer(model).data

    class Query(serializers.Serializer):
        user_id = serializers.CharField(required=True, label=_("User ID"))
        name = serializers.CharField(required=False, max_length=64, label=_('model name'))
        model_type = serializers.CharField(required=False, label=_('model type'))
        model_name = serializers.CharField(required=False, label=_('base model'))
        provider = serializers.CharField(required=False, label=_('provider'))
        create_user = serializers.CharField(required=False, label=_('create user'))
        workspace_id = serializers.CharField(required=False, label=_('workspace id'))

        @staticmethod
        def is_x_pack_ee():
            workspace_user_role_mapping_model = DatabaseModelManage.get_model("workspace_user_role_mapping")
            role_permission_mapping_model = DatabaseModelManage.get_model("role_permission_mapping_model")
            return workspace_user_role_mapping_model is not None and role_permission_mapping_model is not None

        def list(self, workspace_id, with_valid):
            if with_valid:
                self.is_valid(raise_exception=True)
            user_id = self.data.get("user_id")
            workspace_manage = is_workspace_manage(user_id, workspace_id)
            query_params = self._build_query_params(workspace_id, workspace_manage, user_id)
            is_x_pack_ee = self.is_x_pack_ee()
            result = native_search(query_params,
                                   select_string=get_file_content(
                                       os.path.join(PROJECT_DIR, "apps", "models_provider", 'sql',
                                                    'list_model.sql' if workspace_manage else (
                                                        'list_model_user_ee.sql' if is_x_pack_ee else 'list_model_user.sql')
                                                    )))
            return ResourceMappingSerializer().get_resource_count(result)

        def share_list(self, workspace_id, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            user_id = self.data.get("user_id")
            query_params = self._build_query_params(workspace_id, False, user_id)
            result = [
                self._build_model_data(
                    model
                ) for model in query_params.get('model_query_set')
            ]
            return ResourceMappingSerializer().get_resource_count(result)

        def model_list(self, workspace_id, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            user_id = self.data.get("user_id")
            workspace_manage = is_workspace_manage(user_id, workspace_id)
            queryset = self._build_query_params(workspace_id, workspace_manage, user_id)
            get_authorized_model = DatabaseModelManage.get_model("get_authorized_model")

            shared_queryset = QuerySet(Model).none()
            if get_authorized_model is not None:
                shared_queryset = self._build_query_params('None', False, user_id)['model_query_set']
                shared_queryset = get_authorized_model(shared_queryset, workspace_id)

            # 构建共享模型和普通模型列表
            shared_model = [self._build_model_data(model) for model in shared_queryset]

            is_x_pack_ee = self.is_x_pack_ee()
            normal_model = native_search(
                queryset,
                select_string=get_file_content(
                    os.path.join(
                        PROJECT_DIR, "apps", "models_provider", 'sql',
                        'list_model.sql' if workspace_manage else (
                            'list_model_user_ee.sql' if is_x_pack_ee else 'list_model_user.sql')
                    )
                )
            )
            return {
                "shared_model": shared_model,
                "model": normal_model
            }

        def _build_query_params(self, workspace_id, workspace_manage: bool, user_id):
            queryset = QuerySet(Model)
            if workspace_id:
                queryset = queryset.filter(workspace_id=workspace_id)
            for field in ['name', 'model_type', 'model_name', 'provider', 'create_user']:
                value = self.data.get(field)
                if value is not None:
                    if field == 'name':
                        queryset = queryset.filter(**{f'{field}__icontains': value})
                    elif field == 'create_user':
                        queryset = queryset.filter(user_id=value)
                    else:
                        queryset = queryset.filter(**{field: value})
            queryset = queryset.order_by("-create_time")
            return {
                'model_query_set': queryset,
                'workspace_user_resource_permission_query_set': QuerySet(WorkspaceUserResourcePermission).filter(
                    auth_target_type="MODEL",
                    workspace_id=workspace_id,
                    user_id=user_id)} if (
                not workspace_manage) else {
                'model_query_set': queryset,
            }

        def _build_model_data(self, model):
            return {
                'id': str(model.id),
                'provider': model.provider,
                'name': model.name,
                'model_type': model.model_type,
                'model_name': model.model_name,
                'status': model.status,
                'meta': model.meta,
                'user_id': model.user_id,
                'username': model.user.username,
                'nick_name': model.user.nick_name,
            }

        def page(self, current_page, page_size):
            pass

    class ModelParams(serializers.Serializer):
        id = serializers.UUIDField(required=True, label=_('model id'))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            model = QuerySet(Model).filter(id=self.data.get("id")).first()
            if model is None:
                raise AppApiException(500, _("Model does not exist"))

        def get_model_params(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            model_id = self.data.get('id')
            model = QuerySet(Model).filter(id=model_id).first()
            return model.model_params_form

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


class WorkspaceSharedModelSerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=True, label=_('workspace id'))
    name = serializers.CharField(required=False, max_length=64, label=_('model name'))
    model_type = serializers.CharField(required=False, label=_('model type'))
    model_name = serializers.CharField(required=False, label=_('base model'))
    provider = serializers.CharField(required=False, label=_('provider'))
    create_user = serializers.CharField(required=False, label=_('create user'))

    def get_share_model_list(self):
        self.is_valid(raise_exception=True)
        workspace_id = self.data.get('workspace_id')

        queryset = self._build_queryset(workspace_id)

        return [
            {
                'id': str(model.id),
                'provider': model.provider,
                'name': model.name,
                'model_type': model.model_type,
                'model_name': model.model_name,
                'status': model.status,
                'meta': model.meta,
                'user_id': model.user_id,
                'nick_name': model.user.nick_name,
                'username': model.user.username
            }
            for model in queryset.order_by("-create_time")
        ]

    def _build_queryset(self, workspace_id):
        queryset = QuerySet(Model)
        if workspace_id:
            get_authorized_model = DatabaseModelManage.get_model("get_authorized_model")
            if get_authorized_model is not None:
                queryset = get_authorized_model(queryset, workspace_id)

        for field in ['name', 'model_type', 'model_name', 'provider', 'create_user']:
            value = self.data.get(field)
            if value is not None:
                if field == 'name':
                    queryset = queryset.filter(**{f'{field}__icontains': value})
                elif field == 'create_user':
                    queryset = queryset.filter(user_id=value)
                else:
                    queryset = queryset.filter(**{field: value})

        return queryset
