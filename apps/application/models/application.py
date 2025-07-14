# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application.py
    @date：2025/5/7 15:29
    @desc:
"""
import uuid_utils.compat as uuid
from django.db import models
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from common.mixins.app_model_mixin import AppModelMixin
from knowledge.models import Knowledge
from models_provider.models import Model
from users.models import User


class ApplicationFolder(MPTTModel, AppModelMixin):
    id = models.CharField(primary_key=True, max_length=64, editable=False, verbose_name="主键id")
    name = models.CharField(max_length=64, verbose_name="文件夹名称", db_index=True)
    desc = models.CharField(max_length=200, null=True, blank=True, verbose_name="描述")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, db_constraint=False, blank=True, null=True)
    workspace_id = models.CharField(max_length=64, verbose_name="工作空间id", default="default", db_index=True)
    parent = TreeForeignKey('self', on_delete=models.DO_NOTHING, null=True, blank=True, related_name='children')

    class Meta:
        db_table = "application_folder"

    class MPTTMeta:
        order_insertion_by = ['name']


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
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    workspace_id = models.CharField(max_length=64, verbose_name="工作空间id", default="default", db_index=True)
    folder = models.ForeignKey(ApplicationFolder, on_delete=models.DO_NOTHING, verbose_name="文件夹id",
                               default='default')
    is_publish = models.BooleanField(verbose_name="是否发布", default=False)
    name = models.CharField(max_length=128, verbose_name="应用名称", db_index=True)
    desc = models.CharField(max_length=512, verbose_name="引用描述", default="")
    prologue = models.CharField(max_length=40960, verbose_name="开场白", default="")
    dialogue_number = models.IntegerField(default=0, verbose_name="会话数量")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, db_constraint=False, blank=True, null=True)
    model = models.ForeignKey(Model, on_delete=models.SET_NULL, db_constraint=False, blank=True, null=True)
    knowledge_setting = models.JSONField(verbose_name="数据集参数设置", default=get_dataset_setting_dict)
    model_setting = models.JSONField(verbose_name="模型参数相关设置", default=get_model_setting_dict)
    model_params_setting = models.JSONField(verbose_name="模型参数相关设置", default=dict)
    tts_model_params_setting = models.JSONField(verbose_name="模型参数相关设置", default=dict)
    problem_optimization = models.BooleanField(verbose_name="问题优化", default=False)
    icon = models.CharField(max_length=256, verbose_name="应用icon", default="./favicon.ico")
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
    publish_time = models.DateTimeField(verbose_name="发布时间", default=None, null=True, blank=True)
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


class ApplicationKnowledgeMapping(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    application = models.ForeignKey(Application, on_delete=models.DO_NOTHING)
    knowledge = models.ForeignKey(Knowledge, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "application_knowledge_mapping"


class ApplicationVersion(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    name = models.CharField(verbose_name="版本名称", max_length=128, default="")
    publish_user_id = models.UUIDField(verbose_name="发布者id", max_length=128, default=None, null=True)
    publish_user_name = models.CharField(verbose_name="发布者名称", max_length=128, default="")
    workspace_id = models.CharField(max_length=64, verbose_name="工作空间id", default="default", db_index=True)
    application_name = models.CharField(max_length=128, verbose_name="应用名称")
    desc = models.CharField(max_length=512, verbose_name="引用描述", default="")
    prologue = models.CharField(max_length=40960, verbose_name="开场白", default="")
    dialogue_number = models.IntegerField(default=0, verbose_name="会话数量")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, db_constraint=False, blank=True, null=True)
    model_id = models.UUIDField(verbose_name="大语言模型", blank=True, null=True)
    knowledge_setting = models.JSONField(verbose_name="数据集参数设置", default=get_dataset_setting_dict)
    model_setting = models.JSONField(verbose_name="模型参数相关设置", default=get_model_setting_dict)
    model_params_setting = models.JSONField(verbose_name="模型参数相关设置", default=dict)
    tts_model_params_setting = models.JSONField(verbose_name="模型参数相关设置", default=dict)
    problem_optimization = models.BooleanField(verbose_name="问题优化", default=False)
    icon = models.CharField(max_length=256, verbose_name="应用icon", default="./favicon.ico")
    work_flow = models.JSONField(verbose_name="工作流数据", default=dict)
    type = models.CharField(verbose_name="应用类型", choices=ApplicationTypeChoices.choices,
                            default=ApplicationTypeChoices.SIMPLE, max_length=256)
    problem_optimization_prompt = models.CharField(verbose_name="问题优化提示词", max_length=102400, blank=True,
                                                   null=True,
                                                   default="()里面是用户问题,根据上下文回答揣测用户问题({question}) 要求: 输出一个补全问题,并且放在<data></data>标签中")
    tts_model_id = models.UUIDField(verbose_name="文本转语音模型id",
                                    blank=True, null=True)
    stt_model_id = models.UUIDField(verbose_name="语音转文本模型id",
                                    blank=True, null=True)
    tts_model_enable = models.BooleanField(verbose_name="语音合成模型是否启用", default=False)
    stt_model_enable = models.BooleanField(verbose_name="语音识别模型是否启用", default=False)
    tts_type = models.CharField(verbose_name="语音播放类型", max_length=20, default="BROWSER")
    tts_autoplay = models.BooleanField(verbose_name="自动播放", default=False)
    stt_autosend = models.BooleanField(verbose_name="自动发送", default=False)
    clean_time = models.IntegerField(verbose_name="清理时间", default=180)
    file_upload_enable = models.BooleanField(verbose_name="文件上传是否启用", default=False)
    file_upload_setting = models.JSONField(verbose_name="文件上传相关设置", default=dict)

    class Meta:
        db_table = "application_version"
