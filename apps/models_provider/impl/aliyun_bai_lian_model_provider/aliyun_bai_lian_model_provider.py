# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： aliyun_bai_lian_model_provider.py
    @date：2024/9/9 17:43
    @desc:
"""
import os

from common.utils.common import get_file_content
from models_provider.base_model_provider import ModelProvideInfo, ModelTypeConst, ModelInfo, IModelProvider, \
    ModelInfoManage
from models_provider.impl.aliyun_bai_lian_model_provider.credential.stt.asr_stt import AliyunBaiLianAsrSTTModelCredential
from models_provider.impl.aliyun_bai_lian_model_provider.credential.embedding import \
    AliyunBaiLianEmbeddingCredential
from models_provider.impl.aliyun_bai_lian_model_provider.credential.image import QwenVLModelCredential
from models_provider.impl.aliyun_bai_lian_model_provider.credential.itv import ImageToVideoModelCredential
from models_provider.impl.aliyun_bai_lian_model_provider.credential.llm import BaiLianLLMModelCredential
from models_provider.impl.aliyun_bai_lian_model_provider.credential.stt.omni_stt import AliyunBaiLianOmiSTTModelCredential
from models_provider.impl.aliyun_bai_lian_model_provider.credential.reranker import \
    AliyunBaiLianRerankerCredential
from models_provider.impl.aliyun_bai_lian_model_provider.credential.stt import AliyunBaiLianSTTModelCredential, \
    AliyunBaiLianDefaultSTTModelCredential
from models_provider.impl.aliyun_bai_lian_model_provider.credential.tti import QwenTextToImageModelCredential
from models_provider.impl.aliyun_bai_lian_model_provider.credential.tts import AliyunBaiLianTTSModelCredential
from models_provider.impl.aliyun_bai_lian_model_provider.credential.ttv import TextToVideoModelCredential
from models_provider.impl.aliyun_bai_lian_model_provider.model.stt.asr_stt import AliyunBaiLianAsrSpeechToText
from models_provider.impl.aliyun_bai_lian_model_provider.model.embedding import AliyunBaiLianEmbedding
from models_provider.impl.aliyun_bai_lian_model_provider.model.image import QwenVLChatModel
from models_provider.impl.aliyun_bai_lian_model_provider.model.llm import BaiLianChatModel
from models_provider.impl.aliyun_bai_lian_model_provider.model.stt.omni_stt import AliyunBaiLianOmiSpeechToText
from models_provider.impl.aliyun_bai_lian_model_provider.model.reranker import AliyunBaiLianReranker
from models_provider.impl.aliyun_bai_lian_model_provider.model.stt import AliyunBaiLianSpeechToText, \
    AliyunBaiLianDefaultSpeechToText
from models_provider.impl.aliyun_bai_lian_model_provider.model.tti import QwenTextToImageModel
from models_provider.impl.aliyun_bai_lian_model_provider.model.tts import AliyunBaiLianTextToSpeech
from maxkb.conf import PROJECT_DIR
from django.utils.translation import gettext as _, gettext

from models_provider.impl.aliyun_bai_lian_model_provider.model.ttv import GenerationVideoModel

aliyun_bai_lian_model_credential = AliyunBaiLianRerankerCredential()
aliyun_bai_lian_tts_model_credential = AliyunBaiLianTTSModelCredential()
aliyun_bai_lian_stt_model_credential = AliyunBaiLianSTTModelCredential()
aliyun_bai_lian_omi_stt_model_credential = AliyunBaiLianOmiSTTModelCredential()
aliyun_bai_lian_asr_stt_model_credential = AliyunBaiLianAsrSTTModelCredential()
aliyun_bai_lian_default_stt_model_credential = AliyunBaiLianDefaultSTTModelCredential()
aliyun_bai_lian_embedding_model_credential = AliyunBaiLianEmbeddingCredential()
aliyun_bai_lian_llm_model_credential = BaiLianLLMModelCredential()
qwenvl_model_credential = QwenVLModelCredential()
qwentti_model_credential = QwenTextToImageModelCredential()
aliyun_bai_lian_ttv_model_credential = TextToVideoModelCredential()
aliyun_bai_lian_itv_model_credential = ImageToVideoModelCredential()

model_info_list = [ModelInfo('gte-rerank-v2',
                             _('With the GTE-Rerank text sorting series model developed by Alibaba Tongyi Lab, developers can integrate high-quality text retrieval and sorting through the LlamaIndex framework.'),
                             ModelTypeConst.RERANKER, aliyun_bai_lian_model_credential, AliyunBaiLianReranker),
                   ModelInfo('paraformer-realtime-v2',
                             _('Chinese (including various dialects such as Cantonese), English, Japanese, and Korean support free switching between multiple languages.'),
                             ModelTypeConst.STT, aliyun_bai_lian_stt_model_credential, AliyunBaiLianSpeechToText),
                   ModelInfo('cosyvoice-v1',
                             _('CosyVoice is based on a new generation of large generative speech models, which can predict emotions, intonation, rhythm, etc. based on context, and has better anthropomorphic effects.'),
                             ModelTypeConst.TTS, aliyun_bai_lian_tts_model_credential, AliyunBaiLianTextToSpeech),
                   ModelInfo('text-embedding-v1',
                             _("Universal text vector is Tongyi Lab's multi-language text unified vector model based on the LLM base. It provides high-level vector services for multiple mainstream languages around the world and helps developers quickly convert text data into high-quality vector data."),
                             ModelTypeConst.EMBEDDING, aliyun_bai_lian_embedding_model_credential,
                             AliyunBaiLianEmbedding),
                   ModelInfo('qwen3-0.6b', '', ModelTypeConst.LLM, aliyun_bai_lian_llm_model_credential,
                             BaiLianChatModel),
                   ModelInfo('qwen3-1.7b', '', ModelTypeConst.LLM, aliyun_bai_lian_llm_model_credential,
                             BaiLianChatModel),
                   ModelInfo('qwen3-4b', '', ModelTypeConst.LLM, aliyun_bai_lian_llm_model_credential,
                             BaiLianChatModel),
                   ModelInfo('qwen3-8b', '', ModelTypeConst.LLM, aliyun_bai_lian_llm_model_credential,
                             BaiLianChatModel),
                   ModelInfo('qwen3-14b', '', ModelTypeConst.LLM, aliyun_bai_lian_llm_model_credential,
                             BaiLianChatModel),
                   ModelInfo('qwen3-32b', '', ModelTypeConst.LLM, aliyun_bai_lian_llm_model_credential,
                             BaiLianChatModel),
                   ModelInfo('qwen3-30b-a3b', '', ModelTypeConst.LLM, aliyun_bai_lian_llm_model_credential,
                             BaiLianChatModel),
                   ModelInfo('qwen3-235b-a22b', '', ModelTypeConst.LLM, aliyun_bai_lian_llm_model_credential,
                             BaiLianChatModel),

                   ModelInfo('qwen-turbo', '', ModelTypeConst.LLM, aliyun_bai_lian_llm_model_credential,
                             BaiLianChatModel),
                   ModelInfo('qwen-plus', '', ModelTypeConst.LLM, aliyun_bai_lian_llm_model_credential,
                             BaiLianChatModel),
                   ModelInfo('qwen-max', '', ModelTypeConst.LLM, aliyun_bai_lian_llm_model_credential,
                             BaiLianChatModel),
                   ModelInfo('qwen-omni-turbo',
                             _('The Qwen Omni series model supports inputting multiple modalities of data, including video, audio, images, and text, and outputting audio and text.'),
                             ModelTypeConst.STT, aliyun_bai_lian_omi_stt_model_credential,
                             AliyunBaiLianOmiSpeechToText),
                   ModelInfo('qwen2.5-omni-7b',
                             _('The Qwen Omni series model supports inputting multiple modalities of data, including video, audio, images, and text, and outputting audio and text.'),
                             ModelTypeConst.STT, aliyun_bai_lian_omi_stt_model_credential,
                             AliyunBaiLianOmiSpeechToText),
                   ModelInfo('qwen-audio-asr',
                             _('The Qwen Audio based end-to-end speech recognition model supports audio recognition within 3 minutes. At present, it mainly supports Chinese and English recognition.'),
                             ModelTypeConst.STT, aliyun_bai_lian_asr_stt_model_credential,
                             AliyunBaiLianAsrSpeechToText),
                   ]

module_info_vl_list = [
    ModelInfo('qwen-vl-max', '', ModelTypeConst.IMAGE, qwenvl_model_credential, QwenVLChatModel),
    ModelInfo('qwen-vl-max-0809', '', ModelTypeConst.IMAGE, qwenvl_model_credential, QwenVLChatModel),
    ModelInfo('qwen-vl-plus-0809', '', ModelTypeConst.IMAGE, qwenvl_model_credential, QwenVLChatModel),
]
module_info_tti_list = [
    ModelInfo('wanx-v1',
              _('Tongyi Wanxiang - a large image model for text generation, supports bilingual input in Chinese and English, and supports the input of reference pictures for reference content or reference style migration. Key styles include but are not limited to watercolor, oil painting, Chinese painting, sketch, flat illustration, two-dimensional, and 3D. Cartoon.'),
              ModelTypeConst.TTI, qwentti_model_credential, QwenTextToImageModel),
]
model_info_ttv_list = [
    ModelInfo('wan2.2-t2v-plus', '', ModelTypeConst.TTV, aliyun_bai_lian_ttv_model_credential,
              GenerationVideoModel),
    ModelInfo('wanx2.1-t2v-turbo', '', ModelTypeConst.TTV, aliyun_bai_lian_ttv_model_credential,
              GenerationVideoModel),
    ModelInfo('wanx2.1-t2v-plus', '', ModelTypeConst.TTV, aliyun_bai_lian_ttv_model_credential,
              GenerationVideoModel),
]
module_info_itv_list = [
    ModelInfo('wan2.2-i2v-flash', '', ModelTypeConst.ITV, aliyun_bai_lian_itv_model_credential,
              GenerationVideoModel),
    ModelInfo('wan2.2-i2v-plus', '', ModelTypeConst.ITV, aliyun_bai_lian_itv_model_credential,
              GenerationVideoModel),
    ModelInfo('wanx2.1-i2v-plus', '', ModelTypeConst.ITV, aliyun_bai_lian_itv_model_credential,
              GenerationVideoModel),
    ModelInfo('wanx2.1-i2v-turbo', '', ModelTypeConst.ITV, aliyun_bai_lian_itv_model_credential,
              GenerationVideoModel),
]

model_info_manage = (
    ModelInfoManage.builder()
    .append_model_info_list(model_info_list)
    .append_model_info_list(module_info_vl_list)
    .append_default_model_info(module_info_vl_list[0])
    .append_model_info_list(module_info_tti_list)
    .append_default_model_info(module_info_tti_list[0])
    .append_default_model_info(model_info_list[1])
    .append_default_model_info(ModelInfo('default',
                             _('default'),
                             ModelTypeConst.STT, aliyun_bai_lian_default_stt_model_credential,
                             AliyunBaiLianDefaultSpeechToText))
    .append_default_model_info(model_info_list[3])
    .append_default_model_info(model_info_list[4])
    .append_default_model_info(model_info_list[0])
    .append_model_info_list(model_info_ttv_list)
    .append_default_model_info(model_info_ttv_list[0])
    .append_model_info_list(module_info_itv_list)
    .append_default_model_info(module_info_itv_list[0])
    .build()
)


class AliyunBaiLianModelProvider(IModelProvider):

    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='aliyun_bai_lian_model_provider', name=gettext('Alibaba Cloud Bailian'),
                                icon=get_file_content(
                                    os.path.join(PROJECT_DIR, "apps", 'models_provider', 'impl',
                                                 'aliyun_bai_lian_model_provider',
                                                 'icon',
                                                 'aliyun_bai_lian_icon_svg')))
