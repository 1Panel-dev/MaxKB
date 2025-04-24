# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： application.py
    @date：2023/9/25 14:24
    @desc:
"""
import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from langchain.schema import HumanMessage, AIMessage
from django.utils.translation import gettext as _
from common.encoder.encoder import SystemEncoder
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
    return {
        'prompt': Application.get_default_model_prompt(),
        'no_references_prompt': '{question}',
        'reasoning_content_start': '<think>',
        'reasoning_content_end': '</think>',
        'reasoning_content_enable': False,
    }


class Application(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    name = models.CharField(max_length=128, verbose_name="应用名称")
    desc = models.CharField(max_length=512, verbose_name="引用描述", default="")
    prologue = models.CharField(max_length=40960, verbose_name="开场白", default="")
    dialogue_number = models.IntegerField(default=0, verbose_name="会话数量")
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    model = models.ForeignKey(Model, on_delete=models.SET_NULL, db_constraint=False, blank=True, null=True)
    dataset_setting = models.JSONField(verbose_name="数据集参数设置", default=get_dataset_setting_dict)
    model_setting = models.JSONField(verbose_name="模型参数相关设置", default=get_model_setting_dict)
    model_params_setting = models.JSONField(verbose_name="模型参数相关设置", default=dict)
    tts_model_params_setting = models.JSONField(verbose_name="模型参数相关设置", default=dict)
    problem_optimization = models.BooleanField(verbose_name="问题优化", default=False)
    icon = models.CharField(max_length=256, verbose_name="应用icon", default="/ui/favicon.ico")
    work_flow = models.JSONField(verbose_name="工作流数据", default=dict)
    type = models.CharField(verbose_name="应用类型", choices=ApplicationTypeChoices.choices,
                            default=ApplicationTypeChoices.SIMPLE, max_length=256)
    problem_optimization_prompt = models.CharField(verbose_name="问题优化提示词", max_length=102400, blank=True,
                                                   null=True,
                                                   default="()里面是用户问题,根据上下文回答揣测用户问题({question}) 要求: 输出一个补全问题,并且放在<data></data>标签中")
    tts_model = models.ForeignKey(Model, related_name='tts_model_id', on_delete=models.SET_NULL, db_constraint=False,
                                  blank=True, null=True)
    stt_model = models.ForeignKey(Model, related_name='stt_model_id', on_delete=models.SET_NULL, db_constraint=False,
                                  blank=True, null=True)
    tts_model_enable = models.BooleanField(verbose_name="语音合成模型是否启用", default=False)
    stt_model_enable = models.BooleanField(verbose_name="语音识别模型是否启用", default=False)
    tts_type = models.CharField(verbose_name="语音播放类型", max_length=20, default="BROWSER")
    tts_autoplay = models.BooleanField(verbose_name="自动播放", default=False)
    stt_autosend = models.BooleanField(verbose_name="自动发送", default=False)
    clean_time = models.IntegerField(verbose_name="清理时间", default=180)
    file_upload_enable = models.BooleanField(verbose_name="文件上传是否启用", default=False)
    file_upload_setting = models.JSONField(verbose_name="文件上传相关设置", default=dict)

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
    name = models.CharField(verbose_name="版本名称", max_length=128, default="")
    publish_user_id = models.UUIDField(verbose_name="发布者id", max_length=128, default=None, null=True)
    publish_user_name = models.CharField(verbose_name="发布者名称", max_length=128, default="")
    work_flow = models.JSONField(verbose_name="工作流数据", default=dict)

    class Meta:
        db_table = "application_work_flow_version"


class ApplicationDatasetMapping(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    dataset = models.ForeignKey(DataSet, on_delete=models.CASCADE)

    class Meta:
        db_table = "application_dataset_mapping"


def default_asker():
    return {'user_name': '游客'}


class Chat(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    abstract = models.CharField(max_length=1024, verbose_name="摘要")
    asker = models.JSONField(verbose_name="访问者", default=default_asker, encoder=SystemEncoder)
    client_id = models.UUIDField(verbose_name="客户端id", default=None, null=True)
    is_deleted = models.BooleanField(verbose_name="", default=False)

    class Meta:
        db_table = "application_chat"


class VoteChoices(models.TextChoices):
    """订单类型"""
    UN_VOTE = -1, '未投票'
    STAR = 0, '赞同'
    TRAMPLE = 1, '反对'


class ChatRecord(AppModelMixin):
    """
    对话日志 详情
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    vote_status = models.CharField(verbose_name='投票', max_length=10, choices=VoteChoices.choices,
                                   default=VoteChoices.UN_VOTE)
    problem_text = models.CharField(max_length=10240, verbose_name="问题")
    answer_text = models.CharField(max_length=40960, verbose_name="答案")
    answer_text_list = ArrayField(verbose_name="改进标注列表",
                                  base_field=models.JSONField()
                                  , default=list)
    message_tokens = models.IntegerField(verbose_name="请求token数量", default=0)
    answer_tokens = models.IntegerField(verbose_name="响应token数量", default=0)
    const = models.IntegerField(verbose_name="总费用", default=0)
    details = models.JSONField(verbose_name="对话详情", default=dict, encoder=SystemEncoder)
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
        answer_text = self.answer_text
        if answer_text is None or len(str(answer_text).strip()) == 0:
            answer_text = _(
                'Sorry, no relevant content was found. Please re-describe your problem or provide more information. ')
        return AIMessage(content=answer_text)

    def get_node_details_runtime_node_id(self, runtime_node_id):
        return self.details.get(runtime_node_id, None)

    class Meta:
        db_table = "application_chat_record"
