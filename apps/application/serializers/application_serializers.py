# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： application_serializers.py
    @date：2023/11/7 10:02
    @desc:
"""
import hashlib
import json
import os
import re
import uuid
from functools import reduce
from typing import Dict, List

from django.contrib.postgres.fields import ArrayField
from django.core import cache, validators
from django.core import signing
from django.db import transaction, models
from django.db.models import QuerySet
from django.http import HttpResponse
from django.template import Template, Context
from rest_framework import serializers

from application.flow.workflow_manage import Flow
from application.models import Application, ApplicationDatasetMapping, ApplicationTypeChoices, WorkFlowVersion
from application.models.api_key_model import ApplicationAccessToken, ApplicationApiKey
from common.cache_data.application_access_token_cache import get_application_access_token, del_application_access_token
from common.cache_data.application_api_key_cache import del_application_api_key, get_application_api_key
from common.config.embedding_config import VectorStore
from common.constants.authentication_type import AuthenticationType
from common.db.search import get_dynamics_model, native_search, native_page_search
from common.db.sql_execute import select_list
from common.exception.app_exception import AppApiException, NotFound404, AppUnauthorizedFailed
from common.field.common import UploadedImageField
from common.models.db_model_manage import DBModelManage
from common.util.common import valid_license
from common.util.field_message import ErrMessage
from common.util.file_util import get_file_content
from dataset.models import DataSet, Document, Image
from dataset.serializers.common_serializers import list_paragraph, get_embedding_model_by_dataset_id_list
from embedding.models import SearchMode
from setting.models import AuthOperate
from setting.models.model_management import Model
from setting.serializers.provider_serializers import ModelSerializer
from smartdoc.conf import PROJECT_DIR
from django.conf import settings

chat_cache = cache.caches['chat_cache']


class ModelDatasetAssociation(serializers.Serializer):
    user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("用户id"))
    model_id = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                     error_messages=ErrMessage.char("模型id"))
    dataset_id_list = serializers.ListSerializer(required=False, child=serializers.UUIDField(required=True,
                                                                                             error_messages=ErrMessage.uuid(
                                                                                                 "知识库id")),
                                                 error_messages=ErrMessage.list("知识库列表"))

    def is_valid(self, *, raise_exception=True):
        super().is_valid(raise_exception=True)
        model_id = self.data.get('model_id')
        user_id = self.data.get('user_id')
        if model_id is not None and len(model_id) > 0:
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


class NoReferencesChoices(models.TextChoices):
    """订单类型"""
    ai_questioning = 'ai_questioning', 'ai回答'
    designated_answer = 'designated_answer', '指定回答'


class NoReferencesSetting(serializers.Serializer):
    status = serializers.ChoiceField(required=True, choices=NoReferencesChoices.choices,
                                     error_messages=ErrMessage.char("无引用状态"))
    value = serializers.CharField(required=True, error_messages=ErrMessage.char("提示词"))


class DatasetSettingSerializer(serializers.Serializer):
    top_n = serializers.FloatField(required=True, max_value=100, min_value=1,
                                   error_messages=ErrMessage.float("引用分段数"))
    similarity = serializers.FloatField(required=True, max_value=1, min_value=0,
                                        error_messages=ErrMessage.float("相识度"))
    max_paragraph_char_number = serializers.IntegerField(required=True, min_value=500, max_value=100000,
                                                         error_messages=ErrMessage.integer("最多引用字符数"))
    search_mode = serializers.CharField(required=True, validators=[
        validators.RegexValidator(regex=re.compile("^embedding|keywords|blend$"),
                                  message="类型只支持register|reset_password", code=500)
    ], error_messages=ErrMessage.char("检索模式"))

    no_references_setting = NoReferencesSetting(required=True, error_messages=ErrMessage.base("未引用分段设置"))


class ModelSettingSerializer(serializers.Serializer):
    prompt = serializers.CharField(required=True, max_length=2048, error_messages=ErrMessage.char("提示词"))


class ApplicationWorkflowSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, max_length=64, min_length=1, error_messages=ErrMessage.char("应用名称"))
    desc = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                 max_length=256, min_length=1,
                                 error_messages=ErrMessage.char("应用描述"))
    prologue = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=4096,
                                     error_messages=ErrMessage.char("开场白"))

    @staticmethod
    def to_application_model(user_id: str, application: Dict):

        default_workflow_json = get_file_content(
            os.path.join(PROJECT_DIR, "apps", "application", 'flow', 'default_workflow.json'))
        default_workflow = json.loads(default_workflow_json)
        for node in default_workflow.get('nodes'):
            if node.get('id') == 'base-node':
                node.get('properties')['node_data'] = {"desc": application.get('desc'),
                                                       "name": application.get('name'),
                                                       "prologue": application.get('prologue')}
        return Application(id=uuid.uuid1(),
                           name=application.get('name'),
                           desc=application.get('desc'),
                           prologue="",
                           dialogue_number=0,
                           user_id=user_id, model_id=None,
                           dataset_setting={},
                           model_setting={},
                           problem_optimization=False,
                           type=ApplicationTypeChoices.WORK_FLOW,
                           work_flow=default_workflow
                           )


def get_base_node_work_flow(work_flow):
    node_list = work_flow.get('nodes')
    base_node_list = [node for node in node_list if node.get('id') == 'base-node']
    if len(base_node_list) > 0:
        return base_node_list[-1]
    return None


class ApplicationSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, max_length=64, min_length=1, error_messages=ErrMessage.char("应用名称"))
    desc = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                 max_length=256, min_length=1,
                                 error_messages=ErrMessage.char("应用描述"))
    model_id = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                     error_messages=ErrMessage.char("模型"))
    multiple_rounds_dialogue = serializers.BooleanField(required=True, error_messages=ErrMessage.char("多轮对话"))
    prologue = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=4096,
                                     error_messages=ErrMessage.char("开场白"))
    dataset_id_list = serializers.ListSerializer(required=False, child=serializers.UUIDField(required=True),
                                                 allow_null=True, error_messages=ErrMessage.list("关联知识库"))
    # 数据集相关设置
    dataset_setting = DatasetSettingSerializer(required=True)
    # 模型相关设置
    model_setting = ModelSettingSerializer(required=True)
    # 问题补全
    problem_optimization = serializers.BooleanField(required=True, error_messages=ErrMessage.boolean("问题补全"))
    # 应用类型
    type = serializers.CharField(required=True, error_messages=ErrMessage.char("应用类型"),
                                 validators=[
                                     validators.RegexValidator(regex=re.compile("^SIMPLE|WORK_FLOW$"),
                                                               message="应用类型只支持SIMPLE|WORK_FLOW", code=500)
                                 ]
                                 )

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
            is_draggable = 'false'
            show_guide = 'true'
            float_icon = f"{self.data.get('protocol')}://{self.data.get('host')}/ui/favicon.ico"
            X_PACK_LICENSE_IS_VALID = (settings.XPACK_LICENSE_IS_VALID if hasattr(settings,
                                                                                  'XPACK_LICENSE_IS_VALID') else False)
            application_setting_model = DBModelManage.get_model('application_setting')
            if application_setting_model is not None and X_PACK_LICENSE_IS_VALID:
                application_setting = QuerySet(application_setting_model).filter(
                    application_id=application_access_token.application_id).first()
                if application_setting is not None:
                    is_draggable = 'true' if application_setting.draggable else 'false'
                    if application_setting.float_icon is not None and len(application_setting.float_icon) > 0:
                        float_icon = f"{self.data.get('protocol')}://{self.data.get('host')}{application_setting.float_icon}"
                    show_guide = 'true' if application_setting.show_guide else 'false'

            is_auth = 'true' if application_access_token is not None and application_access_token.is_active else 'false'
            t = Template(content)
            s = t.render(
                Context(
                    {'is_auth': is_auth, 'protocol': self.data.get('protocol'), 'host': self.data.get('host'),
                     'token': self.data.get('token'),
                     'white_list_str': ",".join(
                         application_access_token.white_list if application_access_token.white_list is not None else []),
                     'white_active': 'true' if application_access_token.white_active else 'false',
                     'is_draggable': is_draggable,
                     'float_icon': float_icon,
                     'show_guide': show_guide}))
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
                                                    error_messages=ErrMessage.list("白名单列表")),
            show_source = serializers.BooleanField(required=False,
                                                   error_messages=ErrMessage.boolean("是否显示知识来源"))

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
                del_application_access_token(application_access_token.access_token)
                application_access_token.access_token = hashlib.md5(str(uuid.uuid1()).encode()).hexdigest()[8:24]
            if 'access_num' in instance and instance.get('access_num') is not None:
                application_access_token.access_num = instance.get("access_num")
            if 'white_active' in instance and instance.get('white_active') is not None:
                application_access_token.white_active = instance.get("white_active")
            if 'white_list' in instance and instance.get('white_list') is not None:
                application_access_token.white_list = instance.get('white_list')
            if 'show_source' in instance and instance.get('show_source') is not None:
                application_access_token.show_source = instance.get('show_source')
            application_access_token.save()
            get_application_access_token(application_access_token.access_token, False)
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
                    'white_list': application_access_token.white_list,
                    'show_source': application_access_token.show_source
                    }

    class Authentication(serializers.Serializer):
        access_token = serializers.CharField(required=True, error_messages=ErrMessage.char("access_token"))

        def auth(self, request, with_valid=True):
            token = request.META.get('HTTP_AUTHORIZATION')
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
        model_id = serializers.CharField(required=False, allow_blank=True, allow_null=True,
                                         error_messages=ErrMessage.char("模型"))
        multiple_rounds_dialogue = serializers.BooleanField(required=False,
                                                            error_messages=ErrMessage.boolean("多轮会话"))
        prologue = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=4096,
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
        icon = serializers.CharField(required=False, allow_null=True, error_messages=ErrMessage.char("icon图标"))

    class Create(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("用户id"))

        @valid_license(model=Application, count=5,
                       message='社区版最多支持 5 个应用，如需拥有更多应用，请联系我们（https://fit2cloud.com/）。')
        @transaction.atomic
        def insert(self, application: Dict):
            application_type = application.get('type')
            if 'WORK_FLOW' == application_type:
                return self.insert_workflow(application)
            else:
                return self.insert_simple(application)

        def insert_workflow(self, application: Dict):
            self.is_valid(raise_exception=True)
            user_id = self.data.get('user_id')
            ApplicationWorkflowSerializer(data=application).is_valid(raise_exception=True)
            application_model = ApplicationWorkflowSerializer.to_application_model(user_id, application)
            application_model.save()
            # 插入认证信息
            ApplicationAccessToken(application_id=application_model.id,
                                   access_token=hashlib.md5(str(uuid.uuid1()).encode()).hexdigest()[8:24]).save()
            return ApplicationSerializerModel(application_model).data

        def insert_simple(self, application: Dict):
            self.is_valid(raise_exception=True)
            user_id = self.data.get('user_id')
            ApplicationSerializer(data=application).is_valid(user_id=user_id, raise_exception=True)
            application_model = ApplicationSerializer.Create.to_application_model(user_id, application)
            dataset_id_list = application.get('dataset_id_list', [])
            application_dataset_mapping_model_list = [
                ApplicationSerializer.Create.to_application_dataset_mapping(application_model.id, dataset_id) for
                dataset_id in dataset_id_list]
            # 插入应用
            application_model.save()
            # 插入认证信息
            ApplicationAccessToken(application_id=application_model.id,
                                   access_token=hashlib.md5(str(uuid.uuid1()).encode()).hexdigest()[8:24]).save()
            # 插入关联数据
            QuerySet(ApplicationDatasetMapping).bulk_create(application_dataset_mapping_model_list)
            return ApplicationSerializerModel(application_model).data

        @staticmethod
        def to_application_model(user_id: str, application: Dict):
            return Application(id=uuid.uuid1(), name=application.get('name'), desc=application.get('desc'),
                               prologue=application.get('prologue'),
                               dialogue_number=3 if application.get('multiple_rounds_dialogue') else 0,
                               user_id=user_id, model_id=application.get('model_id'),
                               dataset_setting=application.get('dataset_setting'),
                               model_setting=application.get('model_setting'),
                               problem_optimization=application.get('problem_optimization'),
                               type=ApplicationTypeChoices.SIMPLE,
                               work_flow={}
                               )

        @staticmethod
        def to_application_dataset_mapping(application_id: str, dataset_id: str):
            return ApplicationDatasetMapping(id=uuid.uuid1(), application_id=application_id, dataset_id=dataset_id)

    class HitTest(serializers.Serializer):
        id = serializers.CharField(required=True, error_messages=ErrMessage.uuid("应用id"))
        user_id = serializers.UUIDField(required=False, error_messages=ErrMessage.uuid("用户id"))
        query_text = serializers.CharField(required=True, error_messages=ErrMessage.char("查询文本"))
        top_number = serializers.IntegerField(required=True, max_value=100, min_value=1,
                                              error_messages=ErrMessage.integer("topN"))
        similarity = serializers.FloatField(required=True, max_value=2, min_value=0,
                                            error_messages=ErrMessage.float("相关度"))
        search_mode = serializers.CharField(required=True, validators=[
            validators.RegexValidator(regex=re.compile("^embedding|keywords|blend$"),
                                      message="类型只支持register|reset_password", code=500)
        ], error_messages=ErrMessage.char("检索模式"))

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
            if len(dataset_id_list) == 0:
                return []
            exclude_document_id_list = [str(document.id) for document in
                                        QuerySet(Document).filter(
                                            dataset_id__in=dataset_id_list,
                                            is_active=False)]
            model = get_embedding_model_by_dataset_id_list(dataset_id_list)
            # 向量库检索
            hit_list = vector.hit_test(self.data.get('query_text'), dataset_id_list, exclude_document_id_list,
                                       self.data.get('top_number'),
                                       self.data.get('similarity'),
                                       SearchMode(self.data.get('search_mode')),
                                       model)
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
                query_set = query_set.filter(**{'temp_application.desc__icontains': self.data.get("desc")})
            if "name" in self.data and self.data.get('name') is not None:
                query_set = query_set.filter(**{'temp_application.name__icontains': self.data.get("name")})
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
            if 'dataset_setting' in application:
                application['dataset_setting'] = {'search_mode': 'embedding', 'no_references_setting': {
                    'status': 'ai_questioning',
                    'value': '{question}'}, **application['dataset_setting']}
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
            fields = ['id', 'name', 'desc', 'prologue', 'dialogue_number', 'icon', 'type']

    class IconOperate(serializers.Serializer):
        application_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("应用id"))
        user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("用户id"))
        image = UploadedImageField(required=True, error_messages=ErrMessage.image("图片"))

        def edit(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            application = QuerySet(Application).filter(id=self.data.get('application_id')).first()
            if application is None:
                raise AppApiException(500, '不存在的应用id')
            image_id = uuid.uuid1()
            image = Image(id=image_id, image=self.data.get('image').read(), image_name=self.data.get('image').name)
            image.save()
            application.icon = f'/api/image/{image_id}'
            application.save()
            application_access_token = QuerySet(ApplicationAccessToken).filter(
                application_id=self.data.get('application_id')).first()
            get_application_access_token(application_access_token.access_token, False)
            return {**ApplicationSerializer.Query.reset_application(ApplicationSerializerModel(application).data)}

    class Operate(serializers.Serializer):
        application_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("应用id"))
        user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("用户id"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            if not QuerySet(Application).filter(id=self.data.get('application_id')).exists():
                raise AppApiException(500, '不存在的应用id')

        def list_model(self, model_type=None, with_valid=True):
            if with_valid:
                self.is_valid()
            if model_type is None:
                model_type = "LLM"
            application = QuerySet(Application).filter(id=self.data.get("application_id")).first()
            return ModelSerializer.Query(
                data={'user_id': application.user_id, 'model_type': model_type}).list(
                with_valid=True)

        def delete(self, with_valid=True):
            if with_valid:
                self.is_valid()
            QuerySet(Application).filter(id=self.data.get('application_id')).delete()
            return True

        @transaction.atomic
        def publish(self, instance, with_valid=True):
            if with_valid:
                self.is_valid()
            application = QuerySet(Application).filter(id=self.data.get("application_id")).first()
            work_flow = instance.get('work_flow')
            if work_flow is None:
                raise AppApiException(500, "work_flow是必填字段")
            Flow.new_instance(work_flow).is_valid()
            base_node = get_base_node_work_flow(work_flow)
            if base_node is not None:
                node_data = base_node.get('properties').get('node_data')
                if node_data is not None:
                    application.name = node_data.get('name')
                    application.desc = node_data.get('desc')
                    application.prologue = node_data.get('prologue')
            dataset_list = self.list_dataset(with_valid=False)
            application_dataset_id_list = [str(dataset.get('id')) for dataset in dataset_list]
            dataset_id_list = self.update_reverse_search_node(work_flow, application_dataset_id_list)
            application.work_flow = work_flow
            application.save()
            # 插入知识库关联关系
            self.save_application_mapping(application_dataset_id_list, dataset_id_list, application.id)
            work_flow_version = WorkFlowVersion(work_flow=work_flow, application=application)
            work_flow_version.save()
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
            self.update_search_node(application.work_flow, [str(dataset.get('id')) for dataset in dataset_list])
            return {**ApplicationSerializer.Query.reset_application(ApplicationSerializerModel(application).data),
                    'dataset_id_list': dataset_id_list}

        def get_search_node(self, work_flow):
            if work_flow is None:
                return []
            return [node for node in work_flow.get('nodes', []) if node.get('type', '') == 'search-dataset-node']

        def update_search_node(self, work_flow, user_dataset_id_list: List):
            search_node_list = self.get_search_node(work_flow)
            for search_node in search_node_list:
                node_data = search_node.get('properties', {}).get('node_data', {})
                dataset_id_list = node_data.get('dataset_id_list', [])
                node_data['source_dataset_id_list'] = dataset_id_list
                node_data['dataset_id_list'] = [dataset_id for dataset_id in dataset_id_list if
                                                user_dataset_id_list.__contains__(dataset_id)]

        def update_reverse_search_node(self, work_flow, user_dataset_id_list: List):
            search_node_list = self.get_search_node(work_flow)
            result_dataset_id_list = []
            for search_node in search_node_list:
                node_data = search_node.get('properties', {}).get('node_data', {})
                dataset_id_list = node_data.get('dataset_id_list', [])
                for dataset_id in dataset_id_list:
                    if not user_dataset_id_list.__contains__(dataset_id):
                        raise AppApiException(500, f"未知的知识库id${dataset_id},无法关联")

                source_dataset_id_list = node_data.get('source_dataset_id_list', [])
                source_dataset_id_list = [source_dataset_id for source_dataset_id in source_dataset_id_list if
                                          not user_dataset_id_list.__contains__(source_dataset_id)]
                source_dataset_id_list = list({*source_dataset_id_list, *dataset_id_list})
                node_data['source_dataset_id_list'] = []
                node_data['dataset_id_list'] = source_dataset_id_list
                result_dataset_id_list = [*source_dataset_id_list, *result_dataset_id_list]
            return list(set(result_dataset_id_list))

        def profile(self, with_valid=True):
            if with_valid:
                self.is_valid()
            application_id = self.data.get("application_id")
            application = QuerySet(Application).get(id=application_id)
            application_access_token = QuerySet(ApplicationAccessToken).filter(application_id=application.id).first()
            if application_access_token is None:
                raise AppUnauthorizedFailed(500, "非法用户")
            return ApplicationSerializer.Query.reset_application(
                {**ApplicationSerializer.ApplicationModel(application).data,
                 'show_source': application_access_token.show_source})

        @transaction.atomic
        def edit(self, instance: Dict, with_valid=True):
            if with_valid:
                self.is_valid()
                ApplicationSerializer.Edit(data=instance).is_valid(
                    raise_exception=True)
            application_id = self.data.get("application_id")

            application = QuerySet(Application).get(id=application_id)
            if instance.get('model_id') is None or len(instance.get('model_id')) == 0:
                application.model_id = None
            else:
                model = QuerySet(Model).filter(
                    id=instance.get('model_id')).first()
                if model is None:
                    raise AppApiException(500, "模型不存在")
                if not model.is_permission(application.user_id):
                    raise AppApiException(500, f"沒有权限使用该模型:{model.name}")
            if 'work_flow' in instance:
                # 当前用户可修改关联的知识库列表
                application_dataset_id_list = [str(dataset_dict.get('id')) for dataset_dict in
                                               self.list_dataset(with_valid=False)]
                self.update_reverse_search_node(instance.get('work_flow'), application_dataset_id_list)

            update_keys = ['name', 'desc', 'model_id', 'multiple_rounds_dialogue', 'prologue', 'status',
                           'dataset_setting', 'model_setting', 'problem_optimization',
                           'api_key_is_active', 'icon', 'work_flow']
            for update_key in update_keys:
                if update_key in instance and instance.get(update_key) is not None:
                    if update_key == 'multiple_rounds_dialogue':
                        application.__setattr__('dialogue_number', 0 if not instance.get(update_key) else 3)
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

                self.save_application_mapping(application_dataset_id_list, dataset_id_list, application_id)
            chat_cache.clear_by_application_id(application_id)
            application_access_token = QuerySet(ApplicationAccessToken).filter(application_id=application_id).first()
            # 更新缓存数据
            get_application_access_token(application_access_token.access_token, False)
            return self.one(with_valid=False)

        @staticmethod
        def save_application_mapping(application_dataset_id_list, dataset_id_list, application_id):
            # 需要排除已删除的数据集
            dataset_id_list = [dataset.id for dataset in QuerySet(DataSet).filter(id__in=dataset_id_list)]
            # 删除已经关联的id
            QuerySet(ApplicationDatasetMapping).filter(dataset_id__in=application_dataset_id_list,
                                                       application_id=application_id).delete()
            # 插入
            QuerySet(ApplicationDatasetMapping).bulk_create(
                [ApplicationDatasetMapping(application_id=application_id, dataset_id=dataset_id) for dataset_id in
                 dataset_id_list]) if len(dataset_id_list) > 0 else None

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

            allow_cross_domain = serializers.BooleanField(required=False,
                                                          error_messages=ErrMessage.boolean("是否允许跨域"))

            cross_domain_list = serializers.ListSerializer(required=False,
                                                           child=serializers.CharField(required=True,
                                                                                       error_messages=ErrMessage.char(
                                                                                           "跨域列表")),
                                                           error_messages=ErrMessage.char("跨域地址"))

        class Operate(serializers.Serializer):
            application_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("应用id"))

            api_key_id = serializers.CharField(required=True, error_messages=ErrMessage.char("ApiKeyid"))

            def delete(self, with_valid=True):
                if with_valid:
                    self.is_valid(raise_exception=True)
                api_key_id = self.data.get("api_key_id")
                application_id = self.data.get('application_id')
                application_api_key = QuerySet(ApplicationApiKey).filter(id=api_key_id,
                                                                         application_id=application_id).first()
                del_application_api_key(application_api_key.secret_key)
                application_api_key.delete()

            def edit(self, instance, with_valid=True):
                if with_valid:
                    self.is_valid(raise_exception=True)
                    ApplicationSerializer.ApplicationKeySerializer.Edit(data=instance).is_valid(raise_exception=True)
                api_key_id = self.data.get("api_key_id")
                application_id = self.data.get('application_id')
                application_api_key = QuerySet(ApplicationApiKey).filter(id=api_key_id,
                                                                         application_id=application_id).first()
                if application_api_key is None:
                    raise AppApiException(500, '不存在')
                if 'is_active' in instance and instance.get('is_active') is not None:
                    application_api_key.is_active = instance.get('is_active')
                if 'allow_cross_domain' in instance and instance.get('allow_cross_domain') is not None:
                    application_api_key.allow_cross_domain = instance.get('allow_cross_domain')
                if 'cross_domain_list' in instance and instance.get('cross_domain_list') is not None:
                    application_api_key.cross_domain_list = instance.get('cross_domain_list')
                application_api_key.save()
                # 写入缓存
                get_application_api_key(application_api_key.secret_key, False)
