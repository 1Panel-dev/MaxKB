from unittest.mock import patch

from django.test import SimpleTestCase

from knowledge.task.generate import generate_related_by_paragraph_id_list


class ParagraphGenerationScopeTests(SimpleTestCase):
    @patch("knowledge.task.generate.get_llm_model")
    @patch("knowledge.task.generate.QuerySet")
    def test_incomplete_scope_stops_before_model_use(self, query, model):
        query.return_value.filter.return_value.count.return_value = 0
        generate_related_by_paragraph_id_list.run("doc", ["paragraph"], "model", {}, "", knowledge_id="knowledge")
        query.return_value.filter.assert_any_call(id__in=["paragraph"], document_id="doc", knowledge_id="knowledge")
        model.assert_not_called()
