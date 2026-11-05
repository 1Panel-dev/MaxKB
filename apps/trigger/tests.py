from unittest.mock import MagicMock, call, patch

from django.test import SimpleTestCase

from trigger.serializers.trigger_task import TriggerTaskQuerySerializer


class TriggerTaskQueryTests(SimpleTestCase):
    def test_task_query_filters_workspace_through_trigger_relation(self):
        query_set = MagicMock()
        query_set.filter.return_value = query_set
        query_set.exists.return_value = True

        with patch("trigger.serializers.trigger_task.QuerySet", side_effect=lambda model: query_set):
            serializer = TriggerTaskQuerySerializer(data={"trigger_id": "trigger-1", "workspace_id": "workspace-1"})
            serializer.is_valid(raise_exception=True)
            serializer.get_query_set()

        query_set.filter.assert_has_calls(
            [
                call(trigger_id="trigger-1"),
                call(trigger__workspace_id="workspace-1"),
            ]
        )
        self.assertNotIn(
            call(workspace_id="workspace-1", trigger_id="trigger-1"),
            query_set.filter.call_args_list,
        )
