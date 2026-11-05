from django.test import SimpleTestCase
from folders.tests.move_helpers import ResourceMoveTests
from knowledge.models import KnowledgeFolder
from knowledge.serializers.knowledge import KnowledgeSerializer
from knowledge.views.knowledge import KnowledgeView


class KnowledgeMoveTests(ResourceMoveTests, SimpleTestCase):
    domain = "knowledge"
    view = KnowledgeView
    view_module = "knowledge.views.knowledge"
    view_serializer = "knowledge.views.knowledge.KnowledgeSerializer.Operate"
    batch_view_serializer = "knowledge.views.knowledge.KnowledgeBatchOperateSerializer"
    serializer_class = KnowledgeSerializer.Operate
    serializer_module = "knowledge.serializers.knowledge"
    serializer_id_key = "knowledge_id"
    folder_model = KnowledgeFolder
