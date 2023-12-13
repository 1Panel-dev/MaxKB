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

from common.mixins.app_model_mixin import AppModelMixin
from dataset.models.data_set import DataSet, Paragraph
from embedding.models import SourceType
from setting.models.model_management import Model
from users.models import User


class Application(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    name = models.CharField(max_length=128, verbose_name="应用名称")
    desc = models.CharField(max_length=128, verbose_name="引用描述", default="")
    prologue = models.CharField(max_length=1024, verbose_name="开场白", default="")
    example = ArrayField(verbose_name="示例列表", base_field=models.CharField(max_length=256, blank=True))
    dialogue_number = models.IntegerField(default=0, verbose_name="会话数量")
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    model = models.ForeignKey(Model, on_delete=models.SET_NULL, db_constraint=False, blank=True, null=True)

    class Meta:
        db_table = "application"


class ApplicationDatasetMapping(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    dataset = models.ForeignKey(DataSet, on_delete=models.CASCADE)

    class Meta:
        db_table = "application_dataset_mapping"


class Chat(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    abstract = models.CharField(max_length=256, verbose_name="摘要")

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
    dataset = models.ForeignKey(DataSet, on_delete=models.SET_NULL, verbose_name="数据集", blank=True, null=True)
    paragraph = models.ForeignKey(Paragraph, on_delete=models.SET_NULL, verbose_name="段落id", blank=True, null=True)
    source_id = models.UUIDField(max_length=128, verbose_name="资源id 段落/问题 id ", null=True)
    source_type = models.CharField(verbose_name='资源类型', max_length=2, choices=SourceType.choices,
                                   default=SourceType.PROBLEM, blank=True, null=True)
    message_tokens = models.IntegerField(verbose_name="请求token数量", default=0)
    answer_tokens = models.IntegerField(verbose_name="响应token数量", default=0)
    problem_text = models.CharField(max_length=1024, verbose_name="问题")
    answer_text = models.CharField(max_length=1024, verbose_name="答案")
    improve_paragraph_id_list = ArrayField(verbose_name="改进标注列表",
                                           base_field=models.UUIDField(max_length=128, blank=True)
                                           , default=list)

    index = models.IntegerField(verbose_name="对话下标")

    class Meta:
        db_table = "application_chat_record"
