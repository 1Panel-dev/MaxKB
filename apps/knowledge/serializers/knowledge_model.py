"""Model serializers shared by knowledge and workflow modules."""

from rest_framework import serializers

from knowledge.models import Knowledge


class KnowledgeModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Knowledge
        fields = [
            "id",
            "name",
            "desc",
            "meta",
            "folder_id",
            "type",
            "workspace_id",
            "create_time",
            "update_time",
            "file_size_limit",
            "file_count_limit",
            "embedding_model_id",
        ]
