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

from application.models import VoteChoices, ChatRecord, Chat, ApplicationAccessToken
from application.serializers.application_chat import ChatCountSerializer
from application.serializers.application_chat_record import ChatRecordSerializerModel, \
    ApplicationChatRecordQuerySerializers
from common.db.search import page_search
from common.exception.app_exception import AppApiException
from common.utils.lock import RedisLock


class VoteRequest(serializers.Serializer):
    vote_status = serializers.ChoiceField(choices=VoteChoices.choices,
                                          label=_("Bidding Status"))


class HistoryChatModel(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['id',
                  'application_id',
                  'abstract',
                  'create_time',
                  'update_time']


class VoteSerializer(serializers.Serializer):
    chat_id = serializers.UUIDField(required=True, label=_("Conversation ID"))

    chat_record_id = serializers.UUIDField(required=True,
                                           label=_("Conversation record id"))

    @transaction.atomic
    def vote(self, instance: Dict, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
            VoteRequest(data=instance).is_valid(raise_exception=True)
        rlock = RedisLock()
        if not rlock.try_lock(self.data.get('chat_record_id')):
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
            rlock.un_lock(self.data.get('chat_record_id'))
        ChatCountSerializer(data={'chat_id': self.data.get('chat_id')}).update_chat()
        return True


class HistoricalConversationSerializer(serializers.Serializer):
    application_id = serializers.UUIDField(required=True, label=_('Application ID'))
    chat_user_id = serializers.UUIDField(required=True, label=_('Chat User ID'))

    def get_queryset(self):
        chat_user_id = self.data.get('chat_user_id')
        application_id = self.data.get("application_id")
        return QuerySet(Chat).filter(application_id=application_id, chat_user_id=chat_user_id,
                                     is_deleted=False).order_by('-update_time')

    def list(self):
        self.is_valid(raise_exception=True)
        queryset = self.get_queryset()
        return [HistoryChatModel(r).data for r in queryset]

    def page(self, current_page, page_size):
        self.is_valid(raise_exception=True)
        return page_search(current_page, page_size, self.get_queryset(), lambda r: HistoryChatModel(r).data)


class EditAbstractSerializer(serializers.Serializer):
    abstract = serializers.CharField(required=True, label=_('Abstract'))


class HistoricalConversationOperateSerializer(serializers.Serializer):
    application_id = serializers.UUIDField(required=True, label=_('Application ID'))
    chat_user_id = serializers.UUIDField(required=True, label=_('Chat User ID'))
    chat_id = serializers.UUIDField(required=True, label=_('Chat ID'))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        e = QuerySet(Chat).filter(id=self.data.get('chat_id'), application_id=self.data.get('application_id'),
                                  chat_user_id=self.data.get('chat_user_id')).exists()
        if not e:
            raise AppApiException(500, _('Chat is not exist'))

    def edit_abstract(self, instance, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
            EditAbstractSerializer(data=instance).is_valid(raise_exception=True)

        QuerySet(Chat).filter(id=self.data.get('chat_id'), application_id=self.data.get('application_id'),
                              chat_user_id=self.data.get('chat_user_id')).update(abstract=instance.get('abstract'))
        return True

    def logic_delete(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        QuerySet(Chat).filter(id=self.data.get('chat_id'), application_id=self.data.get('application_id'),
                              chat_user_id=self.data.get('chat_user_id')).update(is_deleted=True)
        return True

    class Clear(serializers.Serializer):
        application_id = serializers.UUIDField(required=True, label=_('Application ID'))
        chat_user_id = serializers.UUIDField(required=True, label=_('Chat User ID'))

        def batch_logic_delete(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            QuerySet(Chat).filter(application_id=self.data.get('application_id'),
                                  chat_user_id=self.data.get('chat_user_id')).update(is_deleted=True)
            return True


class HistoricalConversationRecordSerializer(serializers.Serializer):
    application_id = serializers.UUIDField(required=True, label=_('Application ID'))
    chat_id = serializers.UUIDField(required=True, label=_('Chat ID'))
    chat_user_id = serializers.UUIDField(required=True, label=_('Chat User ID'))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        chat_user_id = self.data.get('chat_user_id')
        application_id = self.data.get("application_id")
        chat_id = self.data.get('chat_id')
        chat_exist = QuerySet(Chat).filter(application_id=application_id, chat_user_id=chat_user_id,
                                           id=chat_id).exists()
        if not chat_exist:
            raise AppApiException(500, _('Non-existent chatID'))

    def get_queryset(self):
        chat_id = self.data.get('chat_id')
        return QuerySet(ChatRecord).filter(chat_id=chat_id).order_by('-create_time')

    def list(self):
        self.is_valid(raise_exception=True)
        queryset = self.get_queryset()
        return [ChatRecordSerializerModel(r).data for r in queryset]

    def page(self, current_page, page_size):
        self.is_valid(raise_exception=True)
        application_access_token = QuerySet(ApplicationAccessToken).filter(
            application_id=self.data.get('application_id')).first()
        show_source = False
        show_exec = False
        if application_access_token is not None:
            show_exec = application_access_token.show_exec
            show_source = application_access_token.show_source
        return ApplicationChatRecordQuerySerializers(
            data={'application_id': self.data.get('application_id'), 'chat_id': self.data.get('chat_id')}).page(
            current_page, page_size, show_source=show_source, show_exec=show_exec)
