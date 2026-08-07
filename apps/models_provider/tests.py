from unittest import TestCase
from unittest.mock import patch

from models_provider.impl.atlas_cloud_model_provider.atlas_cloud_model_provider import AtlasCloudModelProvider
from models_provider.impl.atlas_cloud_model_provider.constants import ATLAS_CLOUD_API_BASE
from models_provider.impl.atlas_cloud_model_provider.credential.llm import AtlasCloudLLMModelCredential
from models_provider.impl.atlas_cloud_model_provider.model.llm import AtlasCloudChatModel


class AtlasCloudModelProviderTest(TestCase):
    def test_provider_metadata(self):
        provider = AtlasCloudModelProvider()

        self.assertIsInstance(provider, AtlasCloudModelProvider)
        self.assertEqual(
            provider.get_model_provide_info().to_dict(),
            {"provider": "model_atlas_cloud_provider", "name": "Atlas Cloud", "icon": ""},
        )

    def test_provider_exposes_current_model_ids(self):
        provider = AtlasCloudModelProvider()

        model_names = {model["name"] for model in provider.get_model_list("LLM")}

        self.assertIn("google/gemini-2.5-flash", model_names)
        self.assertIn("anthropic/claude-sonnet-4.6", model_names)
        self.assertIn("openai/gpt-5.4", model_names)

    def test_credential_defaults_to_atlas_cloud_api(self):
        credential = AtlasCloudLLMModelCredential()

        self.assertEqual(credential.api_base.default_value, ATLAS_CLOUD_API_BASE)

    def test_model_uses_openai_compatible_configuration(self):
        factory = AtlasCloudChatModel.new_instance
        with patch(
            "models_provider.impl.atlas_cloud_model_provider.model.llm.AtlasCloudChatModel"
        ) as model_constructor:
            model = factory(
                "LLM",
                "google/gemini-2.5-flash",
                {"api_key": "test-key", "api_base": ""},
                temperature=0.2,
                streaming=True,
                model_id="internal-id",
            )

        self.assertIs(model, model_constructor.return_value)
        model_constructor.assert_called_once_with(
            model="google/gemini-2.5-flash",
            openai_api_base=ATLAS_CLOUD_API_BASE,
            openai_api_key="test-key",
            temperature=0.2,
        )

    def test_api_key_is_masked(self):
        credential = AtlasCloudLLMModelCredential()

        encrypted = credential.encryption_dict({"api_key": "test-secret-api-key", "api_base": ATLAS_CLOUD_API_BASE})

        self.assertNotEqual(encrypted["api_key"], "test-secret-api-key")
        self.assertEqual(encrypted["api_base"], ATLAS_CLOUD_API_BASE)
