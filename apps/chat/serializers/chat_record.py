# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： chat_record.py
    @date：2025/6/23 11:16
    @desc:
"""
from typing import Dict

from django.db import transaction
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _, gettext
from rest_framework import serializers

from application.models import VoteChoices, ChatRecord
from common.exception.app_exception import AppApiException
from common.utils.lock import try_lock, un_lock


class VoteRequest(serializers.Serializer):
    vote_status = serializers.ChoiceField(choices=VoteChoices.choices,
                                          label=_("Bidding Status"))


class VoteSerializer(serializers.Serializer):
    chat_id = serializers.UUIDField(required=True, label=_("Conversation ID"))

    chat_record_id = serializers.UUIDField(required=True,
                                           label=_("Conversation record id"))

    @transaction.atomic
    def vote(self, instance: Dict, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
            VoteRequest(data=instance).is_valid(raise_exception=True)
        if not try_lock(self.data.get('chat_record_id')):
            raise AppApiException(500,
                                  gettext(
                                      "Voting on the current session minutes, please do not send repeated requests"))
        try:
            chat_record_details_model = QuerySet(ChatRecord).get(id=self.data.get('chat_record_id'),
                                                                 chat_id=self.data.get('chat_id'))
            if chat_record_details_model is None:
                raise AppApiException(500, gettext("Non-existent conversation chat_record_id"))
            vote_status = instance.get("vote_status")
            if chat_record_details_model.vote_status == VoteChoices.UN_VOTE:
                if vote_status == VoteChoices.STAR:
                    # 点赞
                    chat_record_details_model.vote_status = VoteChoices.STAR

                if vote_status == VoteChoices.TRAMPLE:
                    # 点踩
                    chat_record_details_model.vote_status = VoteChoices.TRAMPLE
                chat_record_details_model.save()
            else:
                if vote_status == VoteChoices.UN_VOTE:
                    # 取消点赞
                    chat_record_details_model.vote_status = VoteChoices.UN_VOTE
                    chat_record_details_model.save()
                else:
                    raise AppApiException(500, gettext("Already voted, please cancel first and then vote again"))
        finally:
            un_lock(self.data.get('chat_record_id'))
        return True
