import uuid_utils as uuid
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from knowledge.models import Knowledge, KnowledgeScope, KnowledgeType


class KnowledgeModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Knowledge
        fields = ['id', 'name', 'desc', 'meta', 'module_id', 'type', 'workspace_id', 'create_time', 'update_time']


class KnowledgeBaseCreateRequest(serializers.Serializer):
    name = serializers.CharField(required=True, label=_('knowledge name'))
    desc = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('knowledge description'))
    embedding = serializers.CharField(required=True, label=_('knowledge embedding'))

class KnowledgeWebCreateRequest(serializers.Serializer):
    name = serializers.CharField(required=True, label=_('knowledge name'))
    desc = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('knowledge description'))
    embedding = serializers.CharField(required=True, label=_('knowledge embedding'))


class KnowledgeSerializer(serializers.Serializer):
    class Create(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, label=_('user id'))
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))

        def insert(self, instance, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                KnowledgeBaseCreateRequest(data=instance).is_valid(raise_exception=True)
            knowledge = Knowledge(
                id=uuid.uuid7(),
                name=instance.get('name'),
                workspace_id=self.data.get('workspace_id'),
                desc=instance.get('desc'),
                type=instance.get('type', KnowledgeType.BASE),
                user_id=self.data.get('user_id'),
                scope=KnowledgeScope.WORKSPACE,
                module_id=instance.get('module_id', 'root'),
                embedding_model_id=instance.get('embedding'),
                meta=instance.get('meta', {}),
            )
            knowledge.save()
            return KnowledgeModelSerializer(knowledge).data


class KnowledgeTreeSerializer(serializers.Serializer):
    def get_knowledge_list(self, param):
        pass
