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
from models_provider.base_model_provider import (
    ModelProvideInfo,
    ModelTypeConst,
    ModelInfo,
    IModelProvider,
    ModelInfoManage,
)
from models_provider.impl.aliyun_bai_lian_model_provider.credential.stt.asr_stt import (
    AliyunBaiLianAsrSTTModelCredential,
)
from models_provider.impl.aliyun_bai_lian_model_provider.credential.embedding import AliyunBaiLianEmbeddingCredential
from models_provider.impl.aliyun_bai_lian_model_provider.credential.image import QwenVLModelCredential
from models_provider.impl.aliyun_bai_lian_model_provider.credential.itv import ImageToVideoModelCredential
from models_provider.impl.aliyun_bai_lian_model_provider.credential.llm import BaiLianLLMModelCredential
from models_provider.impl.aliyun_bai_lian_model_provider.credential.stt.omni_stt import (
    AliyunBaiLianOmiSTTModelCredential,
)
from models_provider.impl.aliyun_bai_lian_model_provider.credential.reranker import AliyunBaiLianRerankerCredential
from models_provider.impl.aliyun_bai_lian_model_provider.credential.stt import (
    AliyunBaiLianSTTModelCredential,
    AliyunBaiLianDefaultSTTModelCredential,
)
from models_provider.impl.aliyun_bai_lian_model_provider.credential.tti import QwenTextToImageModelCredential
from models_provider.impl.aliyun_bai_lian_model_provider.credential.tts import AliyunBaiLianTTSModelCredential
from models_provider.impl.aliyun_bai_lian_model_provider.credential.ttv import TextToVideoModelCredential
from models_provider.impl.aliyun_bai_lian_model_provider.model.stt.asr_stt import AliyunBaiLianAsrSpeechToText
from models_provider.impl.aliyun_bai_lian_model_provider.model.embedding import AliyunBaiLianEmbedding
from models_provider.impl.aliyun_bai_lian_model_provider.model.image import QwenVLChatModel
from models_provider.impl.aliyun_bai_lian_model_provider.model.llm import BaiLianChatModel
from models_provider.impl.aliyun_bai_lian_model_provider.model.stt.omni_stt import AliyunBaiLianOmiSpeechToText
from models_provider.impl.aliyun_bai_lian_model_provider.model.reranker import AliyunBaiLianReranker
from models_provider.impl.aliyun_bai_lian_model_provider.model.stt import (
    AliyunBaiLianSpeechToText,
    AliyunBaiLianDefaultSpeechToText,
)
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

model_info_list = [
    ModelInfo(
        "gte-rerank-v2",
        _(
            "With the GTE-Rerank text sorting series model developed by Alibaba Tongyi Lab, developers can integrate high-quality text retrieval and sorting through the LlamaIndex framework."
        ),
        ModelTypeConst.RERANKER,
        aliyun_bai_lian_model_credential,
        AliyunBaiLianReranker,
    ),
    ModelInfo(
        "paraformer-realtime-v2",
        _(
            "Chinese (including various dialects such as Cantonese), English, Japanese, and Korean support free switching between multiple languages."
        ),
        ModelTypeConst.STT,
        aliyun_bai_lian_stt_model_credential,
        AliyunBaiLianSpeechToText,
    ),
    ModelInfo(
        "cosyvoice-v1",
        _(
            "CosyVoice is based on a new generation of large generative speech models, which can predict emotions, intonation, rhythm, etc. based on context, and has better anthropomorphic effects."
        ),
        ModelTypeConst.TTS,
        aliyun_bai_lian_tts_model_credential,
        AliyunBaiLianTextToSpeech,
    ),
    ModelInfo(
        "text-embedding-v1",
        _(
            "Universal text vector is Tongyi Lab's multi-language text unified vector model based on the LLM base. It provides high-level vector services for multiple mainstream languages around the world and helps developers quickly convert text data into high-quality vector data."
        ),
        ModelTypeConst.EMBEDDING,
        aliyun_bai_lian_embedding_model_credential,
        AliyunBaiLianEmbedding,
    ),
    ModelInfo(
        "qwen3.7-plus",
        _(""),
        ModelTypeConst.LLM,
        aliyun_bai_lian_llm_model_credential,
        BaiLianChatModel,
    ),
    ModelInfo(
        "qwen3.6-plus",
        _(""),
        ModelTypeConst.LLM,
        aliyun_bai_lian_llm_model_credential,
        BaiLianChatModel,
    ),
    ModelInfo(
        "qwen3.6-flash",
        _(""),
        ModelTypeConst.LLM,
        aliyun_bai_lian_llm_model_credential,
        BaiLianChatModel,
    ),
    ModelInfo(
        "qwen3.6-max-preview",
        _(""),
        ModelTypeConst.LLM,
        aliyun_bai_lian_llm_model_credential,
        BaiLianChatModel,
    ),
    ModelInfo(
        "qwen3.5-plus",
        _(""),
        ModelTypeConst.LLM,
        aliyun_bai_lian_llm_model_credential,
        BaiLianChatModel,
    ),
    ModelInfo(
        "qwen3.5-flash",
        _(""),
        ModelTypeConst.LLM,
        aliyun_bai_lian_llm_model_credential,
        BaiLianChatModel,
    ),
    ModelInfo(
        "qwen-omni-turbo",
        _(
            "The Qwen Omni series model supports inputting multiple modalities of data, including video, audio, images, and text, and outputting audio and text."
        ),
        ModelTypeConst.STT,
        aliyun_bai_lian_omi_stt_model_credential,
        AliyunBaiLianOmiSpeechToText,
    ),
    ModelInfo(
        "qwen2.5-omni-7b",
        _(
            "The Qwen Omni series model supports inputting multiple modalities of data, including video, audio, images, and text, and outputting audio and text."
        ),
        ModelTypeConst.STT,
        aliyun_bai_lian_omi_stt_model_credential,
        AliyunBaiLianOmiSpeechToText,
    ),
    ModelInfo(
        "qwen-audio-asr",
        _(
            "The Qwen Audio based end-to-end speech recognition model supports audio recognition within 3 minutes. At present, it mainly supports Chinese and English recognition."
        ),
        ModelTypeConst.STT,
        aliyun_bai_lian_asr_stt_model_credential,
        AliyunBaiLianAsrSpeechToText,
    ),
]

module_info_vl_list = [
    ModelInfo("qwen-vl-max", "", ModelTypeConst.IMAGE, qwenvl_model_credential, QwenVLChatModel),
    ModelInfo("qwen-vl-max-0809", "", ModelTypeConst.IMAGE, qwenvl_model_credential, QwenVLChatModel),
    ModelInfo("qwen-vl-plus-0809", "", ModelTypeConst.IMAGE, qwenvl_model_credential, QwenVLChatModel),
]
module_info_tti_list = [
    ModelInfo(
        "wanx-v1",
        _(
            "Tongyi Wanxiang - a large image model for text generation, supports bilingual input in Chinese and English, and supports the input of reference pictures for reference content or reference style migration. Key styles include but are not limited to watercolor, oil painting, Chinese painting, sketch, flat illustration, two-dimensional, and 3D. Cartoon."
        ),
        ModelTypeConst.TTI,
        qwentti_model_credential,
        QwenTextToImageModel,
    ),
]
model_info_ttv_list = [
    ModelInfo("wan2.2-t2v-plus", "", ModelTypeConst.TTV, aliyun_bai_lian_ttv_model_credential, GenerationVideoModel),
    ModelInfo("wanx2.1-t2v-turbo", "", ModelTypeConst.TTV, aliyun_bai_lian_ttv_model_credential, GenerationVideoModel),
    ModelInfo("wanx2.1-t2v-plus", "", ModelTypeConst.TTV, aliyun_bai_lian_ttv_model_credential, GenerationVideoModel),
]
module_info_itv_list = [
    ModelInfo("wan2.2-i2v-flash", "", ModelTypeConst.ITV, aliyun_bai_lian_itv_model_credential, GenerationVideoModel),
    ModelInfo("wan2.2-i2v-plus", "", ModelTypeConst.ITV, aliyun_bai_lian_itv_model_credential, GenerationVideoModel),
    ModelInfo("wanx2.1-i2v-plus", "", ModelTypeConst.ITV, aliyun_bai_lian_itv_model_credential, GenerationVideoModel),
    ModelInfo("wanx2.1-i2v-turbo", "", ModelTypeConst.ITV, aliyun_bai_lian_itv_model_credential, GenerationVideoModel),
]

model_info_manage = (
    ModelInfoManage.builder()
    .append_model_info_list(model_info_list)
    .append_model_info_list(module_info_vl_list)
    .append_default_model_info(module_info_vl_list[0])
    .append_model_info_list(module_info_tti_list)
    .append_default_model_info(module_info_tti_list[0])
    .append_default_model_info(model_info_list[1])
    .append_default_model_info(model_info_list[2])
    .append_default_model_info(
        ModelInfo(
            "default",
            _("default"),
            ModelTypeConst.STT,
            aliyun_bai_lian_default_stt_model_credential,
            AliyunBaiLianDefaultSpeechToText,
        )
    )
    .append_default_model_info(model_info_list[3])
    .append_default_model_info(model_info_list[4])
    .append_default_model_info(model_info_list[0])
    .append_model_info_list(model_info_ttv_list)
    .append_default_model_info(model_info_ttv_list[0])
    .append_model_info_list(module_info_itv_list)
    .append_default_model_info(module_info_itv_list[0])
    .build()
)


def _type_impl_map():
    """各 MaxKB 模型类型对应的凭证实例与实现类（取自内置映射，非按模型名单写死）。"""
    return {
        ModelTypeConst.LLM: (
            aliyun_bai_lian_llm_model_credential,
            BaiLianChatModel,
            _(""),
        ),
        ModelTypeConst.EMBEDDING: (
            aliyun_bai_lian_embedding_model_credential,
            AliyunBaiLianEmbedding,
            _(""),
        ),
        ModelTypeConst.STT: (
            aliyun_bai_lian_stt_model_credential,
            AliyunBaiLianSpeechToText,
            _(""),
        ),
        ModelTypeConst.TTS: (
            aliyun_bai_lian_tts_model_credential,
            AliyunBaiLianTextToSpeech,
            _(""),
        ),
        ModelTypeConst.IMAGE: (qwenvl_model_credential, QwenVLChatModel, _("")),
        ModelTypeConst.TTI: (
            qwentti_model_credential,
            QwenTextToImageModel,
            _(""),
        ),
        ModelTypeConst.RERANKER: (
            aliyun_bai_lian_model_credential,
            AliyunBaiLianReranker,
            _(""),
        ),
        ModelTypeConst.TTV: (
            aliyun_bai_lian_ttv_model_credential,
            GenerationVideoModel,
            _(""),
        ),
        ModelTypeConst.ITV: (
            aliyun_bai_lian_itv_model_credential,
            GenerationVideoModel,
            _(""),
        ),
    }


class AliyunBaiLianModelProvider(IModelProvider):
    @staticmethod
    def _query_base_for(api_base: str):
        """把凭证里的 api_base 转成 /models 列表接口可用的 base 地址。"""
        api_base = (api_base or "").strip()
        if not api_base:
            return "https://dashscope.aliyuncs.com/api/v1"
        base = api_base.rstrip("/")
        # OpenAI 兼容地址（.../compatible-mode/v1）回到原生 /api/v1
        if "/compatible-mode/" in base:
            return base.split("/compatible-mode/")[0] + "/api/v1"
        return base

    def get_model_info_manage(self):
        # 未提供 api_key 时返回内置常用模型；提供了 key 的实时查询见 get_model_list。
        return model_info_manage

    def get_dynamic_model_info_list(self, api_key, api_base, credential=None):
        """DashScope 专有实现：按 capabilities/inference_metadata 精确映射模型类型。"""
        # 模型列表始终走官方 DashScope 接口；compatible-mode 地址归一化回原生 /api/v1。
        items = []
        for base in dict.fromkeys([self._query_base_for(api_base), "https://dashscope.aliyuncs.com/api/v1"]):
            try:
                items = self.get_base_model_list(api_key, base)
            except Exception:
                items = []
            if items:
                break
        if not items:
            return None
        builtin_by_name = {info.name: info for info in self.get_model_info_manage().model_list}
        info_list = []
        seen = set()
        for item in items:
            model_id = item.get("model") or item.get("model_id") or item.get("id") or item.get("name")
            if not model_id or model_id in seen:
                continue
            seen.add(model_id)
            # 内置列表已有的模型直接沿用原有类型与实现，其余按官方 capabilities 判型。
            builtin = builtin_by_name.get(model_id)
            if builtin is not None:
                info_list.append(
                    ModelInfo(model_id, builtin.desc, builtin.model_type, builtin.model_credential, builtin.model_class)
                )
                continue
            model_type = self._model_type_from_item(item)
            impl = _type_impl_map().get(model_type)
            if impl is None:
                continue
            credential_obj, model_class, desc = impl
            info_list.append(ModelInfo(model_id, desc, model_type, credential_obj, model_class))
        return info_list or None

    def get_model_provide_info(self):
        return ModelProvideInfo(
            provider="aliyun_bai_lian_model_provider",
            name=gettext("Alibaba Cloud Bailian"),
            icon=get_file_content(
                os.path.join(
                    PROJECT_DIR,
                    "apps",
                    "models_provider",
                    "impl",
                    "aliyun_bai_lian_model_provider",
                    "icon",
                    "aliyun_bai_lian_icon_svg",
                )
            ),
        )

    @staticmethod
    def get_base_model_list(api_key: str, api_base: str = None):
        """调用阿里云百炼（DashScope）官方 /models 列表接口实时获取可用模型。

        兼容两种返回结构：
        - DashScope：{"output": {"models": [...]}}
        - 网关/OpenAI 风格：{"data": [...]}（如 ai.fit2cloud.cn 网关）
        传入 api_base 时会作为 SDK 的 base_address，否则使用 SDK 默认的
        https://dashscope.aliyuncs.com/api/v1。
        """
        import dashscope

        models = []
        seen = set()
        page_no = 1
        page_size = 100
        while True:
            kwargs = {"page": page_no, "page_size": page_size, "api_key": api_key}
            if api_base:
                kwargs["base_address"] = api_base
            response = dashscope.Models.list(**kwargs)
            if getattr(response, "status_code", None) != 200:
                if models:
                    return models
                return []
            output = response.output or {}
            if isinstance(output, dict):
                page_models = output.get("models") or output.get("data") or []
            elif isinstance(output, list):
                page_models = output
            else:
                page_models = []
            if not page_models:
                break
            new_count = 0
            for item in page_models:
                model_id = item.get("model") or item.get("id") or item.get("model_id") or item.get("name")
                if not model_id or model_id in seen:
                    continue
                seen.add(model_id)
                models.append(item)
                new_count += 1
            if len(page_models) < page_size or new_count == 0:
                break
            page_no += 1
        return models

    @staticmethod
    def _model_type_from_item(item):
        """根据官方 /models 接口返回的 capabilities 与 inference_metadata 判别 MaxKB 模型类型，缺省按 LLM 处理。"""
        caps = {str(c).lower() for c in (item.get("capabilities") or [])}
        meta = item.get("inference_metadata") or {}
        request_modality = meta.get("request_modality") or []
        response_modality = meta.get("response_modality") or []
        if not isinstance(request_modality, (list, tuple)):
            request_modality = [request_modality]
        if not isinstance(response_modality, (list, tuple)):
            response_modality = [response_modality]
        req = {str(x).lower() for x in request_modality}
        model_id = str(item.get("model") or item.get("model_id") or item.get("id") or "").lower()

        # 官方 capabilities 是权威判别字段，优先级最高
        if "tts" in caps:
            return ModelTypeConst.TTS
        if caps & {"asr", "realtime-asr", "realtime-audio-translate"}:
            return ModelTypeConst.STT
        if "ig" in caps:
            return ModelTypeConst.TTI
        if "vg" in caps:
            return ModelTypeConst.ITV if "image" in req else ModelTypeConst.TTV
        if "me" in caps:
            return ModelTypeConst.EMBEDDING
        if "tr" in caps:
            return ModelTypeConst.RERANKER if "rerank" in model_id else ModelTypeConst.EMBEDDING
        if "vu" in caps and not (caps & {"tg", "reasoning"}):
            return ModelTypeConst.IMAGE
        if caps & {"tg", "reasoning"}:
            return ModelTypeConst.LLM
        if caps:
            return ModelTypeConst.LLM

        # 网关/OpenAI 风格返回 type 字段（无 capabilities），按其映射类型
        item_type = str(item.get("type") or "").lower()
        type_map = {
            "embedding": ModelTypeConst.EMBEDDING,
            "text": ModelTypeConst.LLM,
            "image": ModelTypeConst.IMAGE,
            "audio": ModelTypeConst.STT,
            "tts": ModelTypeConst.TTS,
            "rerank": ModelTypeConst.RERANKER,
            "video": ModelTypeConst.TTV,
        }
        if item_type in type_map:
            return type_map[item_type]

        # 兜底：仅当 capabilities 缺失时按输入/输出模态推断
        resp = {str(x).lower() for x in response_modality}
        if any(k in resp for k in ("video",)):
            return ModelTypeConst.ITV if "image" in req else ModelTypeConst.TTV
        if "image" in resp:
            return ModelTypeConst.TTI
        if "audio" in req and "text" in resp:
            return ModelTypeConst.STT
        return ModelTypeConst.LLM
