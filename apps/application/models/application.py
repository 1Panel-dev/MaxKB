# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： application.py
    @date：2023/9/25 14:24
    @desc:
"""
import datetime
import json
import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from langchain.schema import HumanMessage, AIMessage

from common.mixins.app_model_mixin import AppModelMixin
from dataset.models.data_set import DataSet
from setting.models.model_management import Model
from users.models import User


class ApplicationTypeChoices(models.TextChoices):
    """订单类型"""
    SIMPLE = 'SIMPLE', '简易'
    WORK_FLOW = 'WORK_FLOW', '工作流'


def get_dataset_setting_dict():
    return {'top_n': 3, 'similarity': 0.6, 'max_paragraph_char_number': 5000, 'search_mode': 'embedding',
            'no_references_setting': {
                'status': 'ai_questioning',
                'value': '{question}'
            }}


def get_model_setting_dict():
    return {'prompt': Application.get_default_model_prompt()}


class Application(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    name = models.CharField(max_length=128, verbose_name="应用名称")
    desc = models.CharField(max_length=512, verbose_name="引用描述", default="")
    prologue = models.CharField(max_length=4096, verbose_name="开场白", default="")
    dialogue_number = models.IntegerField(default=0, verbose_name="会话数量")
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    model = models.ForeignKey(Model, on_delete=models.SET_NULL, db_constraint=False, blank=True, null=True)
    dataset_setting = models.JSONField(verbose_name="数据集参数设置", default=get_dataset_setting_dict)
    model_setting = models.JSONField(verbose_name="模型参数相关设置", default=get_model_setting_dict)
    problem_optimization = models.BooleanField(verbose_name="问题优化", default=False)
    icon = models.CharField(max_length=256, verbose_name="应用icon", default="/ui/favicon.ico")
    work_flow = models.JSONField(verbose_name="工作流数据", default=dict)
    type = models.CharField(verbose_name="应用类型", choices=ApplicationTypeChoices.choices,
                            default=ApplicationTypeChoices.SIMPLE, max_length=256)

    @staticmethod
    def get_default_model_prompt():
        return ('已知信息：'
                '\n{data}'
                '\n回答要求：'
                '\n- 如果你不知道答案或者没有从获取答案，请回答“没有在知识库中查找到相关信息，建议咨询相关技术支持或参考官方文档进行操作”。'
                '\n- 避免提及你是从<data></data>中获得的知识。'
                '\n- 请保持答案与<data></data>中描述的一致。'
                '\n- 请使用markdown 语法优化答案的格式。'
                '\n- <data></data>中的图片链接、链接地址和脚本语言请完整返回。'
                '\n- 请使用与问题相同的语言来回答。'
                '\n问题：'
                '\n{question}')

    class Meta:
        db_table = "application"


class WorkFlowVersion(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    work_flow = models.JSONField(verbose_name="工作流数据", default=dict)

    class Meta:
        db_table = "application_work_flow_version"


class ApplicationDatasetMapping(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    dataset = models.ForeignKey(DataSet, on_delete=models.CASCADE)

    class Meta:
        db_table = "application_dataset_mapping"


class Chat(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    abstract = models.CharField(max_length=1024, verbose_name="摘要")
    client_id = models.UUIDField(verbose_name="客户端id", default=None, null=True)
    is_deleted = models.BooleanField(verbose_name="", default=False)

    class Meta:
        db_table = "application_chat"


class VoteChoices(models.TextChoices):
    """订单类型"""
    UN_VOTE = -1, '未投票'
    STAR = 0, '赞同'
    TRAMPLE = 1, '反对'


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self, obj)


class ChatRecord(AppModelMixin):
    """
    对话日志 详情
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    vote_status = models.CharField(verbose_name='投票', max_length=10, choices=VoteChoices.choices,
                                   default=VoteChoices.UN_VOTE)
    problem_text = models.CharField(max_length=1024, verbose_name="问题")
    answer_text = models.CharField(max_length=40960, verbose_name="答案")
    message_tokens = models.IntegerField(verbose_name="请求token数量", default=0)
    answer_tokens = models.IntegerField(verbose_name="响应token数量", default=0)
    const = models.IntegerField(verbose_name="总费用", default=0)
    details = models.JSONField(verbose_name="对话详情", default=dict, encoder=DateEncoder)
    improve_paragraph_id_list = ArrayField(verbose_name="改进标注列表",
                                           base_field=models.UUIDField(max_length=128, blank=True)
                                           , default=list)
    run_time = models.FloatField(verbose_name="运行时长", default=0)
    index = models.IntegerField(verbose_name="对话下标")

    def get_human_message(self):
        if 'problem_padding' in self.details:
            return HumanMessage(content=self.details.get('problem_padding').get('padding_problem_text'))
        return HumanMessage(content=self.problem_text)

    def get_ai_message(self):
        return AIMessage(content=self.answer_text)

    class Meta:
        db_table = "application_chat_record"
