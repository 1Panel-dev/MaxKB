from unittest.mock import patch

from django.test import TestCase
from common.auth.struct.auth import Auth
from common.utils.workflow_reference import get_authorized_tool_ids
from tools.models import Tool, ToolFolder, ToolScope
from users.models import User


class SharedToolAccessTests(TestCase):
    def test_shared_tool_requires_access_to_the_receiving_workspace(self):
        user = User.objects.create(username="shared-tool-user")
        folder, _ = ToolFolder.objects.get_or_create(id="default", defaults={"name": "default"})
        shared = Tool.objects.create(name="shared", folder=folder, workspace_id="None", scope=ToolScope.SHARED)
        ids = [str(shared.id)]
        with patch(
            "common.utils.workflow_reference.DatabaseModelManage.get_model", return_value=lambda tools, ws: tools
        ):
            with patch("common.utils.workflow_reference.get_auth", return_value=Auth(set(), {})):
                self.assertEqual(get_authorized_tool_ids(user.id, "team", ids), [])
            with patch("common.utils.workflow_reference.get_auth", return_value=Auth({"USER:w:team"}, {})):
                self.assertEqual(get_authorized_tool_ids(user.id, "team", ids), ids)
