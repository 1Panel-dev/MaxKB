# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： application_serializers.py
    @date：2023/11/7 10:02
    @desc:
"""
import hashlib
import os
import uuid
from typing import Dict

from django.contrib.postgres.fields import ArrayField
from django.core import cache
from django.core import signing
from django.db import transaction, models
from django.db.models import QuerySet
from rest_framework import serializers

from application.models import Application, ApplicationDatasetMapping
from application.models.api_key_model import ApplicationAccessToken, ApplicationApiKey
from common.constants.authentication_type import AuthenticationType
from common.db.search import get_dynamics_model, native_search, native_page_search
from common.db.sql_execute import select_list
from common.exception.app_exception import AppApiException, NotFound404, AppAuthenticationFailed
from common.util.file_util import get_file_content
from dataset.models import DataSet
from setting.models import AuthOperate
from setting.models.model_management import Model
from setting.models_provider.constants.model_provider_constants import ModelProvideConstants
from smartdoc.conf import PROJECT_DIR
from smartdoc.settings import JWT_AUTH

token_cache = cache.caches['token_cache']


class ModelDatasetAssociation(serializers.Serializer):
    user_id = serializers.UUIDField(required=True)
    model_id = serializers.CharField(required=True)
    dataset_id_list = serializers.ListSerializer(required=False, child=serializers.UUIDField(required=True))

    def is_valid(self, *, raise_exception=True):
        super().is_valid(raise_exception=True)
        model_id = self.data.get('model_id')
        user_id = self.data.get('user_id')
        if not QuerySet(Model).filter(id=model_id).exists():
            raise AppApiException(500, f'模型不存在【{model_id}】')
        dataset_id_list = list(set(self.data.get('dataset_id_list')))
        exist_dataset_id_list = [str(dataset.id) for dataset in
                                 QuerySet(DataSet).filter(id__in=dataset_id_list, user_id=user_id)]
        for dataset_id in dataset_id_list:
            if not exist_dataset_id_list.__contains__(dataset_id):
                raise AppApiException(500, f'数据集id不存在【{dataset_id}】')


class ApplicationSerializerModel(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = "__all__"


class ApplicationSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    desc = serializers.CharField(required=True)
    model_id = serializers.CharField(required=True)
    multiple_rounds_dialogue = serializers.BooleanField(required=True)
    prologue = serializers.CharField(required=True)
    example = serializers.ListSerializer(required=False, child=serializers.CharField(required=True))
    dataset_id_list = serializers.ListSerializer(required=False, child=serializers.UUIDField(required=True))

    class AccessTokenSerializer(serializers.Serializer):
        application_id = serializers.UUIDField(required=True)

        class AccessTokenEditSerializer(serializers.Serializer):
            access_token_reset = serializers.UUIDField(required=False)
            is_active = serializers.BooleanField(required=False)

        def edit(self, instance: Dict, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                ApplicationSerializer.AccessTokenSerializer.AccessTokenEditSerializer(data=instance).is_valid(
                    raise_exception=True)

            application_access_token = QuerySet(ApplicationAccessToken).get(
                application_id=self.data.get('application_id'))
            if 'is_active' in instance:
                application_access_token.is_active = instance.get("is_active")
            if 'access_token_reset' in instance and instance.get('access_token_reset'):
                application_access_token.access_token = hashlib.md5(str(uuid.uuid1()).encode()).hexdigest()[8:24]
            application_access_token.save()
            return self.one(with_valid=False)

        def one(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            application_id = self.data.get("application_id")
            application_access_token = QuerySet(ApplicationAccessToken).filter(
                application_id=application_id).first()
            if application_access_token is None:
                application_access_token = ApplicationAccessToken(application_id=application_id,
                                                                  access_token=hashlib.md5(
                                                                      str(uuid.uuid1()).encode()).hexdigest()[
                                                                               8:24], is_active=True)
                application_access_token.save()
            return {'application_id': application_access_token.application_id,
                    'access_token': application_access_token.access_token,
                    "is_active": application_access_token.is_active}

    class Authentication(serializers.Serializer):
        access_token = serializers.CharField(required=True)

        def auth(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            access_token = self.data.get("access_token")
            application_access_token = QuerySet(ApplicationAccessToken).filter(access_token=access_token).first()
            if application_access_token is not None and application_access_token.is_active:
                token = signing.dumps({'application_id': str(application_access_token.application_id),
                                       'user_id': str(application_access_token.application.user.id),
                                       'access_token': application_access_token.access_token,
                                       'type': AuthenticationType.APPLICATION_ACCESS_TOKEN.value})
                token_cache.set(token, application_access_token, timeout=JWT_AUTH['JWT_EXPIRATION_DELTA'])
                return token
            else:
                raise AppAuthenticationFailed(401, "无效的access_token")

    class Edit(serializers.Serializer):
        name = serializers.CharField(required=False)
        desc = serializers.CharField(required=False)
        model_id = serializers.CharField(required=False)
        multiple_rounds_dialogue = serializers.BooleanField(required=False)
        prologue = serializers.CharField(required=False)
        example = serializers.ListSerializer(required=False, child=serializers.CharField(required=True))
        dataset_id_list = serializers.ListSerializer(required=False, child=serializers.UUIDField(required=True))

    def is_valid(self, *, user_id=None, raise_exception=False):
        super().is_valid(raise_exception=True)
        ModelDatasetAssociation(data={'user_id': user_id, 'model_id': self.data.get('model_id'),
                                      'dataset_id_list': self.data.get('dataset_id_list')}).is_valid()

    class Create(serializers.Serializer):
        user_id = serializers.UUIDField(required=True)

        @transaction.atomic
        def insert(self, application: Dict):
            self.is_valid(raise_exception=True)
            user_id = self.data.get('user_id')
            ApplicationSerializer(data=application).is_valid(user_id=user_id, raise_exception=True)
            application_model = ApplicationSerializer.Create.to_application_model(user_id, application)
            dataset_id_list = application.get('dataset_id_list', [])
            application_dataset_mapping_model_list = [
                ApplicationSerializer.Create.to_application_dateset_mapping(application_model.id, dataset_id) for
                dataset_id in dataset_id_list]
            # 插入应用
            application_model.save()
            # 插入认证信息
            ApplicationAccessToken(application_id=application_model.id,
                                   access_token=hashlib.md5(str(uuid.uuid1()).encode()).hexdigest()[8:24]).save()
            # 插入关联数据
            QuerySet(ApplicationDatasetMapping).bulk_create(application_dataset_mapping_model_list)
            return True

        @staticmethod
        def to_application_model(user_id: str, application: Dict):
            return Application(id=uuid.uuid1(), name=application.get('name'), desc=application.get('desc'),
                               prologue=application.get('prologue'), example=application.get('example'),
                               dialogue_number=3 if application.get('multiple_rounds_dialogue') else 0,
                               status=True, user_id=user_id, model_id=application.get('model_id'),
                               )

        @staticmethod
        def to_application_dateset_mapping(application_id: str, dataset_id: str):
            return ApplicationDatasetMapping(id=uuid.uuid1(), application_id=application_id, dataset_id=dataset_id)

    class Query(serializers.Serializer):
        name = serializers.CharField(required=False)

        desc = serializers.CharField(required=False)

        user_id = serializers.UUIDField(required=True)

        def get_query_set(self):
            user_id = self.data.get("user_id")
            query_set_dict = {}
            query_set = QuerySet(model=get_dynamics_model(
                {'temp_application.name': models.CharField(), 'temp_application.desc': models.CharField()}))
            if "desc" in self.data and self.data.get('desc') is not None:
                query_set = query_set.filter(**{'temp_application.desc__contains': self.data.get("desc")})
            if "name" in self.data and self.data.get('name') is not None:
                query_set = query_set.filter(**{'temp_application.name__contains': self.data.get("name")})

            query_set_dict['default_sql'] = query_set

            query_set_dict['application_custom_sql'] = QuerySet(model=get_dynamics_model(
                {'application.user_id': models.CharField(),
                 })).filter(
                **{'application.user_id': user_id}
            )

            query_set_dict['team_member_permission_custom_sql'] = QuerySet(model=get_dynamics_model(
                {'user_id': models.CharField(),
                 'team_member_permission.auth_target_type': models.CharField(),
                 'team_member_permission.operate': ArrayField(verbose_name="权限操作列表",
                                                              base_field=models.CharField(max_length=256,
                                                                                          blank=True,
                                                                                          choices=AuthOperate.choices,
                                                                                          default=AuthOperate.USE)
                                                              )})).filter(
                **{'user_id': user_id, 'team_member_permission.operate__contains': ['USE'],
                   'team_member_permission.auth_target_type': 'APPLICATION'})

            return query_set_dict

        def list(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            return [ApplicationSerializer.Query.reset_application(a) for a in
                    native_search(self.get_query_set(), select_string=get_file_content(
                        os.path.join(PROJECT_DIR, "apps", "application", 'sql', 'list_application.sql')))]

        @staticmethod
        def reset_application(application: Dict):
            application['multiple_rounds_dialogue'] = True if application.get('dialogue_number') > 0 else False
            del application['dialogue_number']
            return application

        def page(self, current_page: int, page_size: int, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            return native_page_search(current_page, page_size, self.get_query_set(), select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "application", 'sql', 'list_application.sql')),
                                      post_records_handler=ApplicationSerializer.Query.reset_application)

    class ApplicationModel(serializers.ModelSerializer):
        class Meta:
            model = Application
            fields = ['id', 'name', 'desc', 'prologue', 'example', 'dialogue_number', 'status']

    class Operate(serializers.Serializer):
        application_id = serializers.UUIDField(required=True)
        user_id = serializers.UUIDField(required=True)

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            if not QuerySet(Application).filter(id=self.data.get('application_id')).exists():
                raise AppApiException(500, '不存在的应用id')

        def delete(self, with_valid=True):
            if with_valid:
                self.is_valid()
            QuerySet(Application).filter(id=self.data.get('application_id')).delete()
            return True

        def one(self, with_valid=True):
            if with_valid:
                self.is_valid()
            application_id = self.data.get("application_id")
            application = QuerySet(Application).get(id=application_id)
            dataset_list = self.list_dataset(with_valid=False)
            mapping_dataset_id_list = [adm.dataset_id for adm in
                                       QuerySet(ApplicationDatasetMapping).filter(application_id=application_id)]
            dataset_id_list = [d.get('id') for d in
                               list(filter(lambda row: mapping_dataset_id_list.__contains__(row.get('id')),
                                           dataset_list))]
            return {**ApplicationSerializer.Query.reset_application(ApplicationSerializerModel(application).data),
                    'dataset_id_list': dataset_id_list}

        def profile(self, with_valid=True):
            if with_valid:
                self.is_valid()
            application_id = self.data.get("application_id")
            application = QuerySet(Application).get(id=application_id)
            return ApplicationSerializer.Query.reset_application(
                ApplicationSerializer.ApplicationModel(application).data)

        def edit(self, instance: Dict, with_valid=True):
            if with_valid:
                self.is_valid()
                ApplicationSerializer.Edit(data=instance).is_valid(
                    raise_exception=True)
            application_id = self.data.get("application_id")

            application = QuerySet(Application).get(id=application_id)

            model = QuerySet(Model).get(id=instance.get('model_id') if 'model_id' in instance else application.model_id)

            update_keys = ['name', 'desc', 'model_id', 'multiple_rounds_dialogue', 'prologue', 'example']
            for update_key in update_keys:
                if update_key in instance and instance.get(update_key) is not None:
                    if update_key == 'multiple_rounds_dialogue':
                        application.__setattr__('dialogue_number',
                                                0 if instance.get(update_key) else ModelProvideConstants[
                                                    model.provider].value.get_dialogue_number())
                    else:
                        application.__setattr__(update_key, instance.get(update_key))
            application.save()

            if 'dataset_id_list' in instance:
                dataset_id_list = instance.get('dataset_id_list')
                # 当前用户可修改关联的数据集列表
                application_dataset_id_list = [dataset_dict.get('id') for dataset_dict in
                                               self.list_dataset(with_valid=False)]
                for dataset_id in dataset_id_list:
                    if not application_dataset_id_list.__contains__(dataset_id):
                        raise AppApiException(500, f"未知的数据集id${dataset_id},无法关联")

                # 删除已经关联的id
                QuerySet(ApplicationDatasetMapping).filter(dataset_id__in=application_dataset_id_list,
                                                           application_id=application_id).delete()
                # 插入
                QuerySet(ApplicationDatasetMapping).bulk_create(
                    [ApplicationDatasetMapping(application_id=application_id, dataset_id=dataset_id) for dataset_id in
                     dataset_id_list]) if len(dataset_id_list) > 0 else None
            return self.one(with_valid=False)

        def list_dataset(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            application = QuerySet(Application).get(id=self.data.get("application_id"))
            return select_list(get_file_content(
                os.path.join(PROJECT_DIR, "apps", "application", 'sql', 'list_application_dataset.sql')),
                [self.data.get('user_id'), application.user_id, self.data.get('user_id')])

    class ApplicationKeySerializerModel(serializers.ModelSerializer):
        class Meta:
            model = ApplicationApiKey
            fields = "__all__"

    class ApplicationKeySerializer(serializers.Serializer):
        user_id = serializers.UUIDField(required=True)

        application_id = serializers.UUIDField(required=True)

        def generate(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            user_id = self.data.get("user_id")
            application_id = self.data.get("application_id")
            secret_key = 'application-' + hashlib.md5(str(uuid.uuid1()).encode()).hexdigest()
            application_api_key = ApplicationApiKey(id=uuid.uuid1(), secret_key=secret_key, user_id=user_id,
                                                    application_id=application_id)
            application_api_key.save()
            return ApplicationSerializer.ApplicationKeySerializerModel(application_api_key).data

        def list(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            user_id = self.data.get("user_id")
            application_id = self.data.get("application_id")
            return [ApplicationSerializer.ApplicationKeySerializerModel(application_api_key).data for
                    application_api_key in
                    QuerySet(ApplicationApiKey).filter(user_id=user_id, application_id=application_id)]

        class Operate(serializers.Serializer):
            application_id = serializers.UUIDField(required=True)

            api_key_id = serializers.CharField(required=True)

            def delete(self, with_valid=True):
                if with_valid:
                    self.is_valid(raise_exception=True)
                api_key_id = self.data.get("api_key_id")
                application_id = self.data.get('application_id')
                QuerySet(ApplicationApiKey).filter(id=api_key_id,
                                                   application_id=application_id).delete()
