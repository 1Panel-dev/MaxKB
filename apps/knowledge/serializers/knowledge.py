from typing import Dict

import uuid_utils as uuid
from django.db import transaction
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.exception.app_exception import AppApiException
from common.utils.common import valid_license
from knowledge.models import Knowledge, KnowledgeScope, KnowledgeType


class KnowledgeModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Knowledge
        fields = ['id', 'name', 'desc', 'meta', 'folder_id', 'type', 'workspace_id', 'create_time', 'update_time']


class KnowledgeBaseCreateRequest(serializers.Serializer):
    name = serializers.CharField(required=True, label=_('knowledge name'))
    folder_id = serializers.CharField(required=True, label=_('folder id'))
    desc = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('knowledge description'))
    embedding = serializers.CharField(required=True, label=_('knowledge embedding'))


class KnowledgeWebCreateRequest(serializers.Serializer):
    name = serializers.CharField(required=True, label=_('knowledge name'))
    folder_id = serializers.CharField(required=True, label=_('folder id'))
    desc = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('knowledge description'))
    embedding = serializers.CharField(required=True, label=_('knowledge embedding'))
    source_url = serializers.CharField(required=True, label=_('source url'))
    selector = serializers.CharField(required=True, label=_('knowledge selector'))


class KnowledgeSerializer(serializers.Serializer):
    class Create(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, label=_('user id'))
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))

        @valid_license(model=Knowledge, count=50,
                       message=_(
                           'The community version supports up to 50 knowledge bases. If you need more knowledge bases, please contact us (https://fit2cloud.com/).'))
        # @post(post_function=post_embedding_dataset)
        @transaction.atomic
        def save_base(self, instance, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                KnowledgeBaseCreateRequest(data=instance).is_valid(raise_exception=True)
            if QuerySet(Knowledge).filter(workspace_id=self.data.get('workspace_id'),
                                          name=instance.get('name')).exists():
                raise AppApiException(500, _('Knowledge base name duplicate!'))

            knowledge = Knowledge(
                id=uuid.uuid7(),
                name=instance.get('name'),
                workspace_id=self.data.get('workspace_id'),
                desc=instance.get('desc'),
                type=instance.get('type', KnowledgeType.BASE),
                user_id=self.data.get('user_id'),
                scope=KnowledgeScope.WORKSPACE,
                folder_id=instance.get('folder_id', 'root'),
                embedding_model_id=instance.get('embedding'),
                meta=instance.get('meta', {}),
            )
            knowledge.save()
            return KnowledgeModelSerializer(knowledge).data

        def save_web(self, instance: Dict, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                KnowledgeWebCreateRequest(data=instance).is_valid(raise_exception=True)

            if QuerySet(Knowledge).filter(workspace_id=self.data.get('workspace_id'),
                                          name=instance.get('name')).exists():
                raise AppApiException(500, _('Knowledge base name duplicate!'))

            knowledge_id = uuid.uuid7()
            knowledge = Knowledge(
                id=knowledge_id,
                name=instance.get('name'),
                desc=instance.get('desc'),
                user_id=self.data.get('user_id'),
                type=instance.get('type', KnowledgeType.WEB),
                scope=KnowledgeScope.WORKSPACE,
                folder_id=instance.get('folder_id', 'root'),
                embedding_model_id=instance.get('embedding'),
                meta={
                    'source_url': instance.get('source_url'),
                    'selector': instance.get('selector'),
                    'embedding_model_id': instance.get('embedding')
                },
            )
            knowledge.save()
            # sync_web_knowledge.delay(str(knowledge_id), instance.get('source_url'), instance.get('selector'))
            return {**KnowledgeModelSerializer(knowledge).data,
                    'document_list': []}


class KnowledgeTreeSerializer(serializers.Serializer):
    def get_knowledge_list(self, param):
        pass
