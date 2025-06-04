# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application_chat_log.py
    @date：2025/5/29 17:12
    @desc:
"""
import uuid_utils.compat as uuid
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _
from langchain_core.messages import HumanMessage, AIMessage

from application.models import Application
from common.encoder.encoder import SystemEncoder
from common.mixins.app_model_mixin import AppModelMixin


def default_asker():
    return {'user_name': '游客'}


class Chat(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7(), editable=False, verbose_name="主键id")
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    abstract = models.CharField(max_length=1024, verbose_name="摘要")
    asker = models.JSONField(verbose_name="访问者", default=default_asker, encoder=SystemEncoder)
    client_id = models.UUIDField(verbose_name="客户端id", default=None, null=True)
    is_deleted = models.BooleanField(verbose_name="", default=False)

    class Meta:
        db_table = "application_chat"


class VoteChoices(models.TextChoices):
    """订单类型"""
    UN_VOTE = "-1", '未投票'
    STAR = "0", '赞同'
    TRAMPLE = "1", '反对'


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
