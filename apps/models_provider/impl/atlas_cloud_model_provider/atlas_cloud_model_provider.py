from models_provider.base_model_provider import (
    IModelProvider,
    ModelInfo,
    ModelInfoManage,
    ModelProvideInfo,
    ModelTypeConst,
)
from models_provider.impl.atlas_cloud_model_provider.credential.llm import AtlasCloudLLMModelCredential
from models_provider.impl.atlas_cloud_model_provider.model.llm import AtlasCloudChatModel


atlas_cloud_llm_model_credential = AtlasCloudLLMModelCredential()
atlas_cloud_llm_list = [
    ModelInfo("google/gemini-2.5-flash", "", ModelTypeConst.LLM, atlas_cloud_llm_model_credential, AtlasCloudChatModel),
    ModelInfo("google/gemini-2.5-pro", "", ModelTypeConst.LLM, atlas_cloud_llm_model_credential, AtlasCloudChatModel),
    ModelInfo(
        "anthropic/claude-sonnet-4.6", "", ModelTypeConst.LLM, atlas_cloud_llm_model_credential, AtlasCloudChatModel
    ),
    ModelInfo("openai/gpt-4o", "", ModelTypeConst.LLM, atlas_cloud_llm_model_credential, AtlasCloudChatModel),
    ModelInfo(
        "deepseek-ai/deepseek-v3.2", "", ModelTypeConst.LLM, atlas_cloud_llm_model_credential, AtlasCloudChatModel
    ),
    ModelInfo("moonshotai/kimi-k2.5", "", ModelTypeConst.LLM, atlas_cloud_llm_model_credential, AtlasCloudChatModel),
    ModelInfo("zai-org/glm-5", "", ModelTypeConst.LLM, atlas_cloud_llm_model_credential, AtlasCloudChatModel),
    ModelInfo("openai/gpt-5.4", "", ModelTypeConst.LLM, atlas_cloud_llm_model_credential, AtlasCloudChatModel),
    ModelInfo("qwen/qwen3.7-max", "", ModelTypeConst.LLM, atlas_cloud_llm_model_credential, AtlasCloudChatModel),
]

model_info_manage = (
    ModelInfoManage.builder()
    .append_model_info_list(atlas_cloud_llm_list)
    .append_default_model_info(atlas_cloud_llm_list[0])
    .build()
)


class AtlasCloudModelProvider(IModelProvider):
    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider="model_atlas_cloud_provider", name="Atlas Cloud", icon="")
