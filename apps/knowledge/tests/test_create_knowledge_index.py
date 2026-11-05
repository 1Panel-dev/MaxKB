"""Standalone regression for create_knowledge_index REINDEX path (#7597)."""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[0] if False else Path(__file__).resolve().parents[3]
APPS = ROOT / 'apps'


def _stub(name, **attrs):
    mod = types.ModuleType(name)
    for k, v in attrs.items():
        setattr(mod, k, v)
    sys.modules[name] = mod
    return mod


def load_common():
    # Clear prior
    for k in list(sys.modules):
        if k == 'knowledge' or k.startswith('knowledge.'):
            del sys.modules[k]

    _stub('uuid_utils')
    _stub('uuid_utils.compat', uuid7=lambda: None)
    _stub('django')
    _stub('django.db')
    _stub('django.db.models', QuerySet=MagicMock)
    _stub('django.utils')
    _stub('django.utils.translation', gettext_lazy=lambda x: x)
    _stub('rest_framework', serializers=MagicMock())
    _stub('application')
    _stub('application.flow')
    _stub('application.flow.tools',
          save_workflow_mapping=MagicMock(),
          get_instance_resource=MagicMock(),
          knowledge_instance_field_call_dict=MagicMock(),
          append_default_model_mapping=MagicMock())
    _stub('common')
    _stub('common.config')
    _stub('common.config.embedding_config', ModelManage=MagicMock())
    _stub('common.db')
    _stub('common.db.search', native_search=MagicMock())
    sql_mod = _stub('common.db.sql_execute', sql_execute=MagicMock(), update_execute=MagicMock())
    _stub('common.exception')
    _stub('common.exception.app_exception', AppApiException=type('AppApiException', (Exception,), {}))
    _stub('common.utils')
    _stub('common.utils.common', get_file_content=MagicMock())
    _stub('common.utils.fork', Fork=MagicMock())
    _stub('common.utils.logger', maxkb_logger=MagicMock())
    _stub('maxkb')
    _stub('maxkb.conf', PROJECT_DIR='/tmp')
    _stub('models_provider')
    _stub('models_provider.tools', get_model=MagicMock(), get_model_default_params=MagicMock())
    _stub('system_manage')
    _stub('system_manage.models')
    _stub('system_manage.models.resource_mapping', ResourceMapping=MagicMock(), ResourceType=MagicMock())

    # Package hierarchy for knowledge
    knowledge = _stub('knowledge')
    knowledge.__path__ = [str(APPS / 'knowledge')]
    models = _stub('knowledge.models')
    for attr in ('Document', 'KnowledgeWorkflow', 'KnowledgeWorkflowVersion', 'KnowledgeType',
                 'Paragraph', 'Problem', 'ProblemParagraphMapping', 'Knowledge', 'File'):
        setattr(models, attr, MagicMock())
    serializers_pkg = _stub('knowledge.serializers')
    serializers_pkg.__path__ = [str(APPS / 'knowledge' / 'serializers')]

    spec = importlib.util.spec_from_file_location(
        'knowledge.serializers.common',
        APPS / 'knowledge' / 'serializers' / 'common.py',
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules['knowledge.serializers.common'] = mod
    spec.loader.exec_module(mod)
    return mod


class CreateKnowledgeIndexTests(unittest.TestCase):
    def test_reindexes_when_index_already_exists(self):
        common = load_common()
        kid = '11111111-1111-1111-1111-111111111111'
        with patch.object(common, 'sql_execute', return_value=[{'indexname': f'embedding_hnsw_idx_{kid}'}]), \
             patch.object(common, 'update_execute') as update_execute:
            common.create_knowledge_index(knowledge_id=kid)
            sql = update_execute.call_args.args[0]
            self.assertIn('REINDEX INDEX', sql)
            self.assertIn(kid, sql)

    def test_creates_when_index_missing(self):
        common = load_common()
        kid = '22222222-2222-2222-2222-222222222222'
        with patch.object(common, 'sql_execute', side_effect=[[], [{'dims': 768}]]), \
             patch.object(common, 'update_execute') as update_execute:
            common.create_knowledge_index(knowledge_id=kid)
            sql = update_execute.call_args.args[0]
            self.assertIn('CREATE INDEX', sql)
            self.assertNotIn('REINDEX', sql)


if __name__ == '__main__':
    unittest.main()
