from django.test import SimpleTestCase
from folders.tests.move_helpers import ResourceMoveTests
from tools.models import ToolFolder
from tools.serializers.tool import ToolSerializer
from tools.views.tool import ToolView


class ToolMoveTests(ResourceMoveTests, SimpleTestCase):
    domain = "tool"
    view = ToolView
    view_module = "tools.views.tool"
    view_serializer = "tools.views.tool.ToolSerializer.Operate"
    batch_view_serializer = "tools.views.tool.ToolBatchOperateSerializer"
    serializer_class = ToolSerializer.Operate
    serializer_module = "tools.serializers.tool"
    serializer_id_key = "id"
    folder_model = ToolFolder
