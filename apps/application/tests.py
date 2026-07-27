from types import SimpleNamespace
from unittest.mock import MagicMock

from django.test import SimpleTestCase

from application.flow.common import WorkflowMode
from application.flow.step_node.image_to_video_step_node.i_image_to_video_node import (
    IImageToVideoNode,
    ImageToVideoNodeSerializer,
)


class ImageToVideoNodeTestCase(SimpleTestCase):
    @staticmethod
    def build_node(first_frame_url):
        workflow_manage = MagicMock()
        workflow_manage.flow.workflow_mode = WorkflowMode.APPLICATION
        workflow_manage.get_reference_field.return_value = first_frame_url
        node = IImageToVideoNode(
            SimpleNamespace(id='image-to-video', properties={'node_data': {}}),
            {},
            workflow_manage,
        )
        node.node_params_serializer = SimpleNamespace(data={'first_frame_url': ['source', 'image']})
        node.flow_params_serializer = SimpleNamespace(data={})
        node.execute = MagicMock(return_value='executed')
        return node

    def test_serializer_rejects_empty_first_frame_reference(self):
        serializer = ImageToVideoNodeSerializer(data={'prompt': 'prompt', 'first_frame_url': []})

        self.assertFalse(serializer.is_valid())
        self.assertIn('first_frame_url', serializer.errors)

    def test_empty_first_frame_value_does_not_execute_node(self):
        for empty_value in (None, [], ''):
            with self.subTest(empty_value=empty_value):
                node = self.build_node(empty_value)

                with self.assertRaises(ValueError):
                    node._run()

                node.execute.assert_not_called()

    def test_valid_first_frame_value_executes_node(self):
        for first_frame_url in ('https://example.com/image.png', [{'file_id': 'file-id'}]):
            with self.subTest(first_frame_url=first_frame_url):
                node = self.build_node(first_frame_url)

                result = node._run()

                self.assertEqual(result, 'executed')
                self.assertEqual(node.execute.call_args.kwargs['first_frame_url'], first_frame_url)
