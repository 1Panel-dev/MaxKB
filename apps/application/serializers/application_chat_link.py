"""
    @project: MaxKB
    @Author: niu
    @file: application_chat_link.py
    @date: 2026/2/9 10:50
    @desc:
"""
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.models import Chat, ChatShareLink, ShareLinkType, ChatRecord
from common.exception.app_exception import AppApiException
from common.utils.chat_link_code import UUIDEncoder
import uuid_utils.compat as uuid


class ShareChatRecordModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRecord
        fields = ['id', 'problem_text', 'answer_text', 'answer_text_list', 'create_time']

class ChatRecordShareLinkRequestSerializer(serializers.Serializer):
    chat_record_ids = serializers.ListSerializer(
        child=serializers.UUIDField(),
        required=False,
        allow_empty=False,
        label=_("Chat record IDs")
    )
    is_current_all = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        if not attrs.get('is_current_all') and not attrs.get('chat_record_ids'):
            raise serializers.ValidationError(_('Chat record ids can not be empty'))
        return attrs

class ChatRecordShareLinkSerializer(serializers.Serializer):
    chat_id = serializers.UUIDField(required=True, label=_("Conversation ID"))
    application_id = serializers.UUIDField(required=True, label=_("Application ID"))
    user_id = serializers.UUIDField(required=False, label=_("User ID"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        chat_id = self.data.get('chat_id')
        application_id = self.data.get('application_id')

        chat_query_set = Chat.objects.filter(id=chat_id, application_id=application_id, is_deleted=False)
        if not chat_query_set.exists():
            raise AppApiException(500, _('Chat id does not exist'))

    def generate_link(self, instance, with_valid=True):
        if with_valid:
            request_serializer = ChatRecordShareLinkRequestSerializer(data=instance)
            request_serializer.is_valid(raise_exception=True)
            self.is_valid(raise_exception=True)
            if not instance.get('is_current_all', False):
                chat_record_ids: list[str] = instance.get('chat_record_ids')

                record_count = ChatRecord.objects.filter(id__in=chat_record_ids, chat_id=self.data.get('chat_id')).count()
                if record_count != len(chat_record_ids):
                    raise AppApiException(500, _('Invalid chat record ids'))
        chat_id = self.data.get('chat_id')
        application_id = self.data.get('application_id')
        user_id = self.data.get('user_id')

        is_current_all = instance.get('is_current_all', False)
        if is_current_all:
            sorted_ids = list(
                ChatRecord.objects.filter(chat_id=chat_id).order_by('create_time').values_list('id',flat=True)
            )
        else:
            chat_record_ids: list[str] = instance.get('chat_record_ids')
            sorted_ids = list(ChatRecord.objects.filter(id__in=chat_record_ids).order_by('create_time').values_list('id',flat=True))

        existing = ChatShareLink.objects.filter(
            chat_id=chat_id, application_id=application_id,
            share_type=ShareLinkType.PUBLIC,
            user_id=user_id,
            chat_record_ids=sorted_ids
        ).first()

        if existing:
            return {'link': UUIDEncoder.encode(existing.id)}

        chat_share_link_model = ChatShareLink(
            id=uuid.uuid7(),
            chat_id=chat_id,
            application_id=application_id,
            share_type=ShareLinkType.PUBLIC,
            user_id=user_id,
            chat_record_ids=sorted_ids
        )
        chat_share_link_model.save()

        link = UUIDEncoder.encode(chat_share_link_model.id)

        return {'link': link}


class ChatShareLinkDetailSerializer(serializers.Serializer):
    link = serializers.CharField(required=True, label=_("Link"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)

        link = self.data.get('link')
        share_link_id = UUIDEncoder.decode_to_str(link)

        share_link_query_set = ChatShareLink.objects.filter(id=share_link_id).first()
        if not share_link_query_set:
            raise AppApiException(500, _('Share link does not exist'))
        if share_link_query_set.chat.is_deleted:
            raise AppApiException(500, _('Chat has been deleted'))

        return share_link_query_set

    def get_record_list(self):
        share_link_model = self.is_valid(raise_exception=True)

        chat_record_model_list = ChatRecord.objects.filter(id__in=share_link_model.chat_record_ids,
                                                           chat_id=share_link_model.chat_id).order_by('create_time')

        abstract = Chat.objects.filter(
            id=share_link_model.chat_id
        ).values_list('abstract', flat=True).first()
        chat_record_list = ShareChatRecordModelSerializer(chat_record_model_list, many=True).data

        return {
            'abstract': abstract,
            'chat_record_list': chat_record_list
        }
