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
from functools import reduce
from typing import Dict

from django.contrib.postgres.fields import ArrayField
from django.core import cache
from django.core import signing
from django.db import transaction, models
from django.db.models import QuerySet
from django.http import HttpResponse
from django.template import Template, Context
from rest_framework import serializers

from application.models import Application, ApplicationDatasetMapping
from application.models.api_key_model import ApplicationAccessToken, ApplicationApiKey
from common.config.embedding_config import VectorStore, EmbeddingModel
from common.constants.authentication_type import AuthenticationType
from common.db.search import get_dynamics_model, native_search, native_page_search
from common.db.sql_execute import select_list
from common.exception.app_exception import AppApiException, NotFound404
from common.util.field_message import ErrMessage
from common.util.file_util import get_file_content
from dataset.models import DataSet, Document
from dataset.serializers.common_serializers import list_paragraph
from setting.models import AuthOperate
from setting.models.model_management import Model
from setting.models_provider.constants.model_provider_constants import ModelProvideConstants
from setting.serializers.provider_serializers import ModelSerializer
from smartdoc.conf import PROJECT_DIR

token_cache = cache.caches['token_cache']
chat_cache = cache.caches['chat_cache']


class ModelDatasetAssociation(serializers.Serializer):
    user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("用户id"))
    model_id = serializers.CharField(required=True, error_messages=ErrMessage.char("模型id"))
    dataset_id_list = serializers.ListSerializer(required=False, child=serializers.UUIDField(required=True,
                                                                                             error_messages=ErrMessage.uuid(
                                                                                                 "知识库id")),
                                                 error_messages=ErrMessage.list("知识库列表"))

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
                raise AppApiException(500, f'知识库id不存在【{dataset_id}】')


class ApplicationSerializerModel(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = "__all__"


class DatasetSettingSerializer(serializers.Serializer):
    top_n = serializers.FloatField(required=True, max_value=100, min_value=1,
                                   error_messages=ErrMessage.float("引用分段数"))
    similarity = serializers.FloatField(required=True, max_value=1, min_value=0,
                                        error_messages=ErrMessage.float("相识度"))
    max_paragraph_char_number = serializers.IntegerField(required=True, min_value=500, max_value=10000,
                                                         error_messages=ErrMessage.integer("最多引用字符数"))


class ModelSettingSerializer(serializers.Serializer):
    prompt = serializers.CharField(required=True, max_length=2048, error_messages=ErrMessage.char("提示词"))


class ApplicationSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, max_length=64, min_length=1, error_messages=ErrMessage.char("应用名称"))
    desc = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                 max_length=256, min_length=1,
                                 error_messages=ErrMessage.char("应用描述"))
    model_id = serializers.CharField(required=True, error_messages=ErrMessage.char("模型"))
    multiple_rounds_dialogue = serializers.BooleanField(required=True, error_messages=ErrMessage.char("多轮对话"))
    prologue = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=1024,
                                     error_messages=ErrMessage.char("开场白"))
    dataset_id_list = serializers.ListSerializer(required=False, child=serializers.UUIDField(required=True),
                                                 allow_null=True, error_messages=ErrMessage.list("关联知识库"))
    # 数据集相关设置
    dataset_setting = DatasetSettingSerializer(required=True)
    # 模型相关设置
    model_setting = ModelSettingSerializer(required=True)
    # 问题补全
    problem_optimization = serializers.BooleanField(required=True, error_messages=ErrMessage.boolean("问题补全"))

    def is_valid(self, *, user_id=None, raise_exception=False):
        super().is_valid(raise_exception=True)
        ModelDatasetAssociation(data={'user_id': user_id, 'model_id': self.data.get('model_id'),
                                      'dataset_id_list': self.data.get('dataset_id_list')}).is_valid()

    class Embed(serializers.Serializer):
        host = serializers.CharField(required=True, error_messages=ErrMessage.char("主机"))
        protocol = serializers.CharField(required=True, error_messages=ErrMessage.char("协议"))
        token = serializers.CharField(required=True, error_messages=ErrMessage.char("token"))

        def get_embed(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            index_path = os.path.join(PROJECT_DIR, 'apps', "application", 'template', 'embed.js')
            file = open(index_path, "r", encoding='utf-8')
            content = file.read()
            file.close()
            application_access_token = QuerySet(ApplicationAccessToken).filter(
                access_token=self.data.get('token')).first()

            is_auth = 'true' if application_access_token is not None and application_access_token.is_active else 'false'
            application_access_token = QuerySet(ApplicationAccessToken).filter(
                access_token=self.data.get('token')).first()
            t = Template(content)
            s = t.render(
                Context(
                    {'is_auth': is_auth, 'protocol': self.data.get('protocol'), 'host': self.data.get('host'),
                     'token': self.data.get('token'),
                     'white_list_str': ",".join(
                         application_access_token.white_list),
                     'white_active': 'true' if application_access_token.white_active else 'false'}))
            response = HttpResponse(s, status=200, headers={'Content-Type': 'text/javascript'})
            return response

    class AccessTokenSerializer(serializers.Serializer):
        application_id = serializers.UUIDField(required=True, error_messages=ErrMessage.boolean("应用id"))

        class AccessTokenEditSerializer(serializers.Serializer):
            access_token_reset = serializers.BooleanField(required=False,
                                                          error_messages=ErrMessage.boolean("重置Token"))
            is_active = serializers.BooleanField(required=False, error_messages=ErrMessage.boolean("是否开启"))
            access_num = serializers.IntegerField(required=False, max_value=10000,
                                                  min_value=0,
                                                  error_messages=ErrMessage.integer("访问次数"))
            white_active = serializers.BooleanField(required=False, error_messages=ErrMessage.boolean("是否开启白名单"))
            white_list = serializers.ListSerializer(required=False, child=serializers.CharField(required=True,
                                                                                                error_messages=ErrMessage.char(
                                                                                                    "白名单")),
                                                    error_messages=ErrMessage.list("白名单列表"))

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
            if 'access_num' in instance and instance.get('access_num') is not None:
                application_access_token.access_num = instance.get("access_num")
            if 'white_active' in instance and instance.get('white_active') is not None:
                application_access_token.white_active = instance.get("white_active")
            if 'white_list' in instance and instance.get('white_list') is not None:
                application_access_token.white_list = instance.get('white_list')
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
                    "is_active": application_access_token.is_active,
                    'access_num': application_access_token.access_num,
                    'white_active': application_access_token.white_active,
                    'white_list': application_access_token.white_list
                    }

    class Authentication(serializers.Serializer):
        access_token = serializers.CharField(required=True, error_messages=ErrMessage.char("access_token"))

        def auth(self, request, with_valid=True):
            token = request.META.get('HTTP_AUTHORIZATION', None)
            token_details = None
            try:
                # 校验token
                if token is not None:
                    token_details = signing.loads(token)
            except Exception as e:
                token = None
            if with_valid:
                self.is_valid(raise_exception=True)
            access_token = self.data.get("access_token")
            application_access_token = QuerySet(ApplicationAccessToken).filter(access_token=access_token).first()
            if application_access_token is not None and application_access_token.is_active:
                if token_details is not None and 'client_id' in token_details and token_details.get(
                        'client_id') is not None:
                    client_id = token_details.get('client_id')
                else:
                    client_id = str(uuid.uuid1())
                token = signing.dumps({'application_id': str(application_access_token.application_id),
                                       'user_id': str(application_access_token.application.user.id),
                                       'access_token': application_access_token.access_token,
                                       'type': AuthenticationType.APPLICATION_ACCESS_TOKEN.value,
                                       'client_id': client_id})
                return token
            else:
                raise NotFound404(404, "无效的access_token")

    class Edit(serializers.Serializer):
        name = serializers.CharField(required=False, max_length=64, min_length=1,
                                     error_messages=ErrMessage.char("应用名称"))
        desc = serializers.CharField(required=False, max_length=256, min_length=1, allow_null=True, allow_blank=True,
                                     error_messages=ErrMessage.char("应用描述"))
        model_id = serializers.CharField(required=False, error_messages=ErrMessage.char("模型"))
        multiple_rounds_dialogue = serializers.BooleanField(required=False,
                                                            error_messages=ErrMessage.boolean("多轮会话"))
        prologue = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=1024,
                                         error_messages=ErrMessage.char("开场白"))
        dataset_id_list = serializers.ListSerializer(required=False, child=serializers.UUIDField(required=True),
                                                     error_messages=ErrMessage.list("关联知识库")
                                                     )
        # 数据集相关设置
        dataset_setting = DatasetSettingSerializer(required=False, allow_null=True,
                                                   error_messages=ErrMessage.json("数据集设置"))
        # 模型相关设置
        model_setting = ModelSettingSerializer(required=False, allow_null=True,
                                               error_messages=ErrMessage.json("模型设置"))
        # 问题补全
        problem_optimization = serializers.BooleanField(required=False, allow_null=True,
                                                        error_messages=ErrMessage.boolean("问题补全"))

    class Create(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("用户id"))

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
                               prologue=application.get('prologue'),
                               dialogue_number=3 if application.get('multiple_rounds_dialogue') else 0,
                               user_id=user_id, model_id=application.get('model_id'),
                               dataset_setting=application.get('dataset_setting'),
                               model_setting=application.get('model_setting'),
                               problem_optimization=application.get('problem_optimization')
                               )

        @staticmethod
        def to_application_dateset_mapping(application_id: str, dataset_id: str):
            return ApplicationDatasetMapping(id=uuid.uuid1(), application_id=application_id, dataset_id=dataset_id)

    class HitTest(serializers.Serializer):
        id = serializers.CharField(required=True, error_messages=ErrMessage.uuid("应用id"))
        user_id = serializers.UUIDField(required=False, error_messages=ErrMessage.uuid("用户id"))
        query_text = serializers.CharField(required=True, error_messages=ErrMessage.char("查询文本"))
        top_number = serializers.IntegerField(required=True, max_value=10, min_value=1,
                                              error_messages=ErrMessage.integer("topN"))
        similarity = serializers.FloatField(required=True, max_value=1, min_value=0,
                                            error_messages=ErrMessage.float("相关度"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            if not QuerySet(Application).filter(id=self.data.get('id')).exists():
                raise AppApiException(500, '不存在的应用id')

        def hit_test(self):
            self.is_valid()
            vector = VectorStore.get_embedding_vector()
            dataset_id_list = [ad.dataset_id for ad in
                               QuerySet(ApplicationDatasetMapping).filter(
                                   application_id=self.data.get('id'))]

            exclude_document_id_list = [str(document.id) for document in
                                        QuerySet(Document).filter(
                                            dataset_id__in=dataset_id_list,
                                            is_active=False)]
            # 向量库检索
            hit_list = vector.hit_test(self.data.get('query_text'), dataset_id_list, exclude_document_id_list,
                                       self.data.get('top_number'),
                                       self.data.get('similarity'),
                                       EmbeddingModel.get_embedding_model())
            hit_dict = reduce(lambda x, y: {**x, **y}, [{hit.get('paragraph_id'): hit} for hit in hit_list], {})
            p_list = list_paragraph([h.get('paragraph_id') for h in hit_list])
            return [{**p, 'similarity': hit_dict.get(p.get('id')).get('similarity'),
                     'comprehensive_score': hit_dict.get(p.get('id')).get('comprehensive_score')} for p in p_list]

    class Query(serializers.Serializer):
        name = serializers.CharField(required=False, error_messages=ErrMessage.char("应用名称"))

        desc = serializers.CharField(required=False, error_messages=ErrMessage.char("应用描述"))

        user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("用户id"))

        def get_query_set(self):
            user_id = self.data.get("user_id")
            query_set_dict = {}
            query_set = QuerySet(model=get_dynamics_model(
                {'temp_application.name': models.CharField(), 'temp_application.desc': models.CharField(),
                 'temp_application.create_time': models.DateTimeField()}))
            if "desc" in self.data and self.data.get('desc') is not None:
                query_set = query_set.filter(**{'temp_application.desc__contains': self.data.get("desc")})
            if "name" in self.data and self.data.get('name') is not None:
                query_set = query_set.filter(**{'temp_application.name__contains': self.data.get("name")})
            query_set = query_set.order_by("-temp_application.create_time")
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
            fields = ['id', 'name', 'desc', 'prologue', 'dialogue_number']

    class Operate(serializers.Serializer):
        application_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("应用id"))
        user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("用户id"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            if not QuerySet(Application).filter(id=self.data.get('application_id')).exists():
                raise AppApiException(500, '不存在的应用id')

        def list_model(self, with_valid=True):
            if with_valid:
                self.is_valid()
            application = QuerySet(Application).filter(id=self.data.get("application_id")).first()
            return ModelSerializer.Query(
                data={'user_id': application.user_id}).list(
                with_valid=True)

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

            model = QuerySet(Model).filter(
                id=instance.get('model_id') if 'model_id' in instance else application.model_id,
                user_id=application.user_id).first()
            if model is None:
                raise AppApiException(500, "模型不存在")

            update_keys = ['name', 'desc', 'model_id', 'multiple_rounds_dialogue', 'prologue', 'status',
                           'dataset_setting', 'model_setting', 'problem_optimization',
                           'api_key_is_active']
            for update_key in update_keys:
                if update_key in instance and instance.get(update_key) is not None:
                    if update_key == 'multiple_rounds_dialogue':
                        application.__setattr__('dialogue_number',
                                                0 if not instance.get(update_key) else ModelProvideConstants[
                                                    model.provider].value.get_dialogue_number())
                    else:
                        application.__setattr__(update_key, instance.get(update_key))
            application.save()

            if 'dataset_id_list' in instance:
                dataset_id_list = instance.get('dataset_id_list')
                # 当前用户可修改关联的知识库列表
                application_dataset_id_list = [str(dataset_dict.get('id')) for dataset_dict in
                                               self.list_dataset(with_valid=False)]
                for dataset_id in dataset_id_list:
                    if not application_dataset_id_list.__contains__(dataset_id):
                        raise AppApiException(500, f"未知的知识库id${dataset_id},无法关联")

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
                [self.data.get('user_id') if self.data.get('user_id') == str(application.user_id) else None,
                 application.user_id, self.data.get('user_id')])

    class ApplicationKeySerializerModel(serializers.ModelSerializer):
        class Meta:
            model = ApplicationApiKey
            fields = "__all__"

    class ApplicationKeySerializer(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("用户id"))

        application_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("应用id"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            application_id = self.data.get("application_id")
            application = QuerySet(Application).filter(id=application_id).first()
            if application is None:
                raise AppApiException(1001, "应用不存在")

        def generate(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            application_id = self.data.get("application_id")
            application = QuerySet(Application).filter(id=application_id).first()
            secret_key = 'application-' + hashlib.md5(str(uuid.uuid1()).encode()).hexdigest()
            application_api_key = ApplicationApiKey(id=uuid.uuid1(), secret_key=secret_key, user_id=application.user_id,
                                                    application_id=application_id)
            application_api_key.save()
            return ApplicationSerializer.ApplicationKeySerializerModel(application_api_key).data

        def list(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            application_id = self.data.get("application_id")
            return [ApplicationSerializer.ApplicationKeySerializerModel(application_api_key).data for
                    application_api_key in
                    QuerySet(ApplicationApiKey).filter(application_id=application_id)]

        class Edit(serializers.Serializer):
            is_active = serializers.BooleanField(required=False, error_messages=ErrMessage.boolean("是否可用"))

        class Operate(serializers.Serializer):
            application_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("应用id"))

            api_key_id = serializers.CharField(required=True, error_messages=ErrMessage.char("ApiKeyid"))

            def delete(self, with_valid=True):
                if with_valid:
                    self.is_valid(raise_exception=True)
                api_key_id = self.data.get("api_key_id")
                application_id = self.data.get('application_id')
                QuerySet(ApplicationApiKey).filter(id=api_key_id,
                                                   application_id=application_id).delete()

            def edit(self, instance, with_valid=True):
                if with_valid:
                    self.is_valid(raise_exception=True)
                    ApplicationSerializer.Edit(data=instance).is_valid(raise_exception=True)

                if 'is_active' in instance and instance.get('is_active') is not None:
                    api_key_id = self.data.get("api_key_id")
                    application_id = self.data.get('application_id')
                    application_api_key = QuerySet(ApplicationApiKey).filter(id=api_key_id,
                                                                             application_id=application_id).first()
                    if application_api_key is None:
                        raise AppApiException(500, '不存在')

                    application_api_key.is_active = instance.get('is_active')
                    application_api_key.save()
