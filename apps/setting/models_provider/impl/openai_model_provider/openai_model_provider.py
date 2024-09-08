# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： openai_model_provider.py
    @date：2024/3/28 16:26
    @desc:
"""
import os

from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import IModelProvider, ModelProvideInfo, ModelInfo, \
    ModelTypeConst, ModelInfoManage
from setting.models_provider.impl.openai_model_provider.credential.embedding import OpenAIEmbeddingCredential
from setting.models_provider.impl.openai_model_provider.credential.llm import OpenAILLMModelCredential
from setting.models_provider.impl.openai_model_provider.credential.stt import OpenAISTTModelCredential
from setting.models_provider.impl.openai_model_provider.model.embedding import OpenAIEmbeddingModel
from setting.models_provider.impl.openai_model_provider.model.llm import OpenAIChatModel
from setting.models_provider.impl.openai_model_provider.model.stt import OpenAISpeechToText
from setting.models_provider.impl.openai_model_provider.model.tts import OpenAITextToSpeech
from smartdoc.conf import PROJECT_DIR

openai_llm_model_credential = OpenAILLMModelCredential()
openai_stt_model_credential = OpenAISTTModelCredential()
model_info_list = [
    ModelInfo('gpt-3.5-turbo', '最新的gpt-3.5-turbo，随OpenAI调整而更新', ModelTypeConst.LLM,
              openai_llm_model_credential, OpenAIChatModel
              ),
    ModelInfo('gpt-4', '最新的gpt-4，随OpenAI调整而更新', ModelTypeConst.LLM, openai_llm_model_credential,
              OpenAIChatModel),
    ModelInfo('gpt-4o', '最新的GPT-4o，比gpt-4-turbo更便宜、更快，随OpenAI调整而更新',
              ModelTypeConst.LLM, openai_llm_model_credential,
              OpenAIChatModel),
    ModelInfo('gpt-4o-mini', '最新的gpt-4o-mini，比gpt-4o更便宜、更快，随OpenAI调整而更新',
            ModelTypeConst.LLM, openai_llm_model_credential,
            OpenAIChatModel),
    ModelInfo('gpt-4-turbo', '最新的gpt-4-turbo，随OpenAI调整而更新', ModelTypeConst.LLM,
              openai_llm_model_credential,
              OpenAIChatModel),
    ModelInfo('gpt-4-turbo-preview', '最新的gpt-4-turbo-preview，随OpenAI调整而更新',
              ModelTypeConst.LLM, openai_llm_model_credential,
              OpenAIChatModel),
    ModelInfo('gpt-3.5-turbo-0125',
              '2024年1月25日的gpt-3.5-turbo快照，支持上下文长度16,385 tokens', ModelTypeConst.LLM,
              openai_llm_model_credential,
              OpenAIChatModel),
    ModelInfo('gpt-3.5-turbo-1106',
              '2023年11月6日的gpt-3.5-turbo快照，支持上下文长度16,385 tokens', ModelTypeConst.LLM,
              openai_llm_model_credential,
              OpenAIChatModel),
    ModelInfo('gpt-3.5-turbo-0613',
              '[Legacy] 2023年6月13日的gpt-3.5-turbo快照，将于2024年6月13日弃用',
              ModelTypeConst.LLM, openai_llm_model_credential,
              OpenAIChatModel),
    ModelInfo('gpt-4o-2024-05-13',
              '2024年5月13日的gpt-4o快照，支持上下文长度128,000 tokens',
              ModelTypeConst.LLM, openai_llm_model_credential,
              OpenAIChatModel),
    ModelInfo('gpt-4-turbo-2024-04-09',
              '2024年4月9日的gpt-4-turbo快照，支持上下文长度128,000 tokens',
              ModelTypeConst.LLM, openai_llm_model_credential,
              OpenAIChatModel),
    ModelInfo('gpt-4-0125-preview', '2024年1月25日的gpt-4-turbo快照，支持上下文长度128,000 tokens',
              ModelTypeConst.LLM, openai_llm_model_credential,
              OpenAIChatModel),
    ModelInfo('gpt-4-1106-preview', '2023年11月6日的gpt-4-turbo快照，支持上下文长度128,000 tokens',
              ModelTypeConst.LLM, openai_llm_model_credential,
              OpenAIChatModel),
    ModelInfo('whisper-1', '',
              ModelTypeConst.STT, openai_stt_model_credential,
              OpenAISpeechToText),
    ModelInfo('tts-1', '',
              ModelTypeConst.TTS, openai_stt_model_credential,
              OpenAITextToSpeech)
]
open_ai_embedding_credential = OpenAIEmbeddingCredential()
model_info_embedding_list = [
    ModelInfo('text-embedding-ada-002', '',
              ModelTypeConst.EMBEDDING, open_ai_embedding_credential,
              OpenAIEmbeddingModel),
    ModelInfo('text-embedding-3-small', '',
              ModelTypeConst.EMBEDDING, open_ai_embedding_credential,
              OpenAIEmbeddingModel),
    ModelInfo('text-embedding-3-large', '',
              ModelTypeConst.EMBEDDING, open_ai_embedding_credential,
              OpenAIEmbeddingModel)
]

model_info_manage = ModelInfoManage.builder().append_model_info_list(model_info_list).append_default_model_info(
    ModelInfo('gpt-3.5-turbo', '最新的gpt-3.5-turbo，随OpenAI调整而更新', ModelTypeConst.LLM,
              openai_llm_model_credential, OpenAIChatModel
              )).append_model_info_list(model_info_embedding_list).append_default_model_info(
    model_info_embedding_list[0]).build()


class OpenAIModelProvider(IModelProvider):

    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_openai_provider', name='OpenAI', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'openai_model_provider', 'icon',
                         'openai_icon_svg')))
