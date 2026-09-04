# coding=utf-8
"""
    llmman (https://github.com/llmmanorg/llmman) is a local model runner that serves the
    Ollama API on port 17434, so the Ollama model classes and credentials are reused as-is.
"""
import os

from common.utils.common import get_file_content
from maxkb.conf import PROJECT_DIR
from models_provider.base_model_provider import ModelInfo, ModelInfoManage, ModelProvideInfo, ModelTypeConst
from models_provider.impl.ollama_model_provider.credential.embedding import OllamaEmbeddingModelCredential
from models_provider.impl.ollama_model_provider.credential.llm import OllamaLLMModelCredential
from models_provider.impl.ollama_model_provider.model.embedding import OllamaEmbedding
from models_provider.impl.ollama_model_provider.model.llm import OllamaChatModel
from models_provider.impl.ollama_model_provider.ollama_model_provider import OllamaModelProvider

llmman_llm_model_credential = OllamaLLMModelCredential()
llmman_embedding_model_credential = OllamaEmbeddingModelCredential()
model_info_list = [
    ModelInfo('gemma4', '', ModelTypeConst.LLM, llmman_llm_model_credential, OllamaChatModel),
    ModelInfo('qwen3.8', '', ModelTypeConst.LLM, llmman_llm_model_credential, OllamaChatModel),
    ModelInfo('hf.co/unsloth/Qwen3.5-0.8B-GGUF', '', ModelTypeConst.LLM, llmman_llm_model_credential,
              OllamaChatModel),
]
embedding_model_info = [
    ModelInfo('hf.co/nomic-ai/nomic-embed-text-v1.5-GGUF', '', ModelTypeConst.EMBEDDING,
              llmman_embedding_model_credential, OllamaEmbedding),
]

model_info_manage = (
    ModelInfoManage.builder()
    .append_model_info_list(model_info_list)
    .append_default_model_info(model_info_list[0])
    .append_model_info_list(embedding_model_info)
    .append_default_model_info(embedding_model_info[0])
    .build()
)


class LlmmanModelProvider(OllamaModelProvider):
    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_llmman_provider', name='llmman', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", 'models_provider', 'impl', 'llmman_model_provider', 'icon',
                         'llmman_icon_svg')))
