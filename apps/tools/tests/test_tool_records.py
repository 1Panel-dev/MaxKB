from unittest.mock import patch

from django.test import TestCase

from knowledge.models.knowledge_action import State
from tools.models import Tool, ToolRecord, ToolType
from tools.serializers.tool import ToolSerializer


class NestedToolRecordTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.child = Tool.objects.create(name="get_weather_info", workspace_id="weather-workspace")
        cls.parent = Tool.objects.create(
            name="get_city_weather", workspace_id=cls.child.workspace_id, tool_type=ToolType.WORKFLOW
        )
        cls.record = ToolRecord.objects.create(
            tool=cls.child,
            workspace_id=cls.child.workspace_id,
            source_type="TOOL",
            source_id=cls.parent.id,
            state=State.SUCCESS,
            meta={"input": {"city": "Hangzhou"}, "output": {"weather": "sunny"}},
        )

    def get_records(self, **filters):
        return ToolSerializer.ToolRecord(
            data={"tool_id": str(self.child.id), "workspace_id": self.child.workspace_id, **filters}
        ).get_tool_records(1, 20)["records"]

    def test_nested_execution_identifies_parent_tool(self):
        records = self.get_records()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["source_type"], "TOOL")
        self.assertEqual(records[0]["source_name"], self.parent.name)
        self.assertEqual(records[0]["source_id"], str(self.parent.id))

    def test_search_matches_parent_tool_name_and_type(self):
        records = self.get_records(source_name="city_weather", source_type="TOOL")
        self.assertEqual([record["id"] for record in records], [str(self.record.id)])
        self.assertEqual(self.get_records(source_name=self.child.name), [])
        self.assertEqual(self.get_records(source_type="APPLICATION"), [])
        self.assertEqual(self.get_records(workspace_id="other-workspace"), [])

    @patch("tools.serializers.tool.cache.get", return_value=None)
    def test_nested_code_tool_detail_keeps_inputs_and_outputs(self, cache_get):
        detail = ToolSerializer.ToolRecord.Operate(
            data={"id": str(self.record.id), "tool_id": str(self.child.id), "workspace_id": self.child.workspace_id}
        ).one()
        self.assertEqual(detail["meta"], self.record.meta)
        self.assertEqual(detail["source_type"], "TOOL")
        self.assertEqual(detail["source_id"], self.parent.id)
