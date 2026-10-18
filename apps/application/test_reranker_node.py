# coding=utf-8
import importlib.util
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from langchain_core.documents import Document


class RerankerDirectAnswerTestCase(unittest.TestCase):
    def test_returns_only_matching_segments_in_ranked_order(self):
        # Isolate Django/model services so the node can be tested without a database.
        model_factory = Mock()
        dependencies = {
            'application.flow.i_step_node': SimpleNamespace(
                NodeResult=lambda node_variable, workflow_variable: SimpleNamespace(node_variable=node_variable)
            ),
            'application.flow.step_node.reranker_node.i_reranker_node': SimpleNamespace(IRerankerNode=object),
            'models_provider.tools': SimpleNamespace(get_model_instance_by_model_workspace_id=model_factory),
        }
        source = Path(__file__).parent / 'flow/step_node/reranker_node/impl/base_reranker_node.py'
        spec = importlib.util.spec_from_file_location('base_reranker_node_under_test', source)
        module = importlib.util.module_from_spec(spec)
        with patch.dict('sys.modules', dependencies):
            spec.loader.exec_module(module)

        for flags in ((True, False, True), (False, True, False), (False, False, False)):
            with self.subTest(flags=flags):
                documents = [
                    {'content': f'segment {index}', 'is_hit_handling_method': flag, 'id': str(index)}
                    for index, flag in enumerate(flags)
                ]
                # Return only scores from the provider; the node restores source metadata.
                model_factory.return_value.compress_documents.return_value = [
                    Document(page_content=f'segment {index}', metadata={'relevance_score': 0.9})
                    for index in (2, 0, 1)
                ]
                node = module.BaseRerankerNode()
                node.context = {}
                node.workflow_manage = Mock()
                node.workflow_manage.get_body.return_value = {'workspace_id': 'workspace'}

                result = node.execute(
                    question='question',
                    reranker_setting={'top_n': 3, 'similarity': 0.6, 'max_paragraph_char_number': 5000},
                    reranker_list=[documents],
                    reranker_model_id='model',
                    show_knowledge=True,
                ).node_variable

                expected_ids = [str(index) for index in (2, 0, 1) if flags[index]]
                direct_segments = result['is_hit_handling_method_list']
                self.assertEqual(len(direct_segments), len(expected_ids))
                self.assertTrue(all(isinstance(segment, dict) for segment in direct_segments))
                self.assertEqual([segment['metadata']['id'] for segment in direct_segments], expected_ids)
                self.assertEqual(len(result['result_list']), 3)
                self.assertEqual(result['result'], 'segment 2segment 0segment 1')


if __name__ == '__main__':
    unittest.main()
