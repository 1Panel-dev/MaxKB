from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from knowledge.models import Problem


class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ['id', 'content', 'knowledge_id', 'create_time', 'update_time']


class ProblemInstanceSerializer(serializers.Serializer):
    id = serializers.CharField(required=False, label=_('problem id'))
    content = serializers.CharField(required=True, max_length=256, label=_('content'))
