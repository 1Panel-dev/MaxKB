import json
from unittest.mock import Mock, patch

from django.test import TestCase

from common.config.embedding_config import ModelManage
from common.utils.rsa_util import rsa_long_encrypt
from models_provider.models import Model
from models_provider.tools import get_model_instance_by_model_workspace_id


class _UncachedModel:
    @staticmethod
    def is_cache_model():
        return False


class ModelCacheInvalidationTests(TestCase):
    def setUp(self):
        ModelManage.cache.clear()

    def tearDown(self):
        ModelManage.cache.clear()

    def test_runtime_uses_credential_saved_by_another_process(self):
        workspace_id = "credential-refresh"
        old_credential = {"auth_value": "before-rotation"}
        new_credential = {"auth_value": "after-rotation"}
        model = Model.objects.create(
            workspace_id=workspace_id,
            name="Qwen VL",
            model_type="LLM",
            model_name="qwen-vl-max",
            provider="aliyun_bai_lian_model_provider",
            credential=rsa_long_encrypt(json.dumps(old_credential)),
        )
        received_credentials = []
        provider = Mock()

        def create_model(_model_type, _model_name, credential, **_kwargs):
            received_credentials.append(credential)
            return _UncachedModel()

        provider.get_model.side_effect = create_model

        with (
            patch("models_provider.tools.get_provider", return_value=provider),
            patch("models_provider.tools.connection.close"),
        ):
            get_model_instance_by_model_workspace_id(str(model.id), workspace_id)

            Model.objects.filter(id=model.id).update(credential=rsa_long_encrypt(json.dumps(new_credential)))

            get_model_instance_by_model_workspace_id(str(model.id), workspace_id)

        self.assertEqual(received_credentials, [old_credential, new_credential])
