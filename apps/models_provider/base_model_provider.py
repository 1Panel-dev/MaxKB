# coding=utf-8

import json
import time

import requests

from abc import ABC, abstractmethod
from enum import Enum
from functools import reduce
from typing import Dict, Iterator, List, Type

from common.exception.app_exception import AppApiException
from common.utils.common import encryption
from django.utils.translation import gettext_lazy as _
from pydantic import BaseModel


class DownModelChunkStatus(Enum):
    success = "success"
    error = "error"
    pulling = "pulling"
    unknown = "unknown"


class ValidCode(Enum):
    valid_error = 500
    model_not_fount = 404


class DownModelChunk:
    def __init__(self, status: DownModelChunkStatus, digest: str, progress: int, details: str, index: int):
        self.details = details
        self.status = status
        self.digest = digest
        self.progress = progress
        self.index = index

    def to_dict(self):
        return {
            "details": self.details,
            "status": self.status.value,
            "digest": self.digest,
            "progress": self.progress,
            "index": self.index,
        }


# 动态模型列表缓存：(provider, api_key, api_base) -> (ModelInfoManage, monotonic 时间戳)
_dynamic_model_manage_cache = {}
_DYNAMIC_MODEL_TTL_SECONDS = 5 * 60
_DYNAMIC_MODEL_CACHE_MAX_SIZE = 512
# 查询失败的 (provider, api_key, api_base, credential 指纹) 短期跳过
_dynamic_model_failed_cache = {}
_DYNAMIC_MODEL_FAILED_TTL_SECONDS = 10 * 60
_DYNAMIC_MODEL_FAILED_CACHE_MAX_SIZE = 512


def _evict_cache(cache: dict, max_size: int):
    """简单的容量上限保护：超出时淘汰最早写入的条目。"""
    while len(cache) > max_size:
        oldest = next(iter(cache))
        cache.pop(oldest, None)


def _model_type_name(model_type):
    """ModelTypeConst 枚举名或字符串，统一作为 impl_map 的 key。"""
    return model_type.name if isinstance(model_type, ModelTypeConst) else str(model_type)


def classify_dynamic_model_id(model_id: str):
    """按模型 id 关键词推断 MaxKB 模型类型，无法识别时按 LLM 处理。"""
    model_id = str(model_id).lower()
    if "embed" in model_id:
        return ModelTypeConst.EMBEDDING
    if "rerank" in model_id:
        return ModelTypeConst.RERANKER
    if any(k in model_id for k in ("whisper", "asr", "transcribe", "paraformer")):
        return ModelTypeConst.STT
    if any(k in model_id for k in ("tts", "speech", "voice", "cosyvoice", "sambert")):
        return ModelTypeConst.TTS
    if any(
        k in model_id for k in ("dall-e", "flux", "stable-diffusion", "sdxl", "wanx", "wan2", "z-image", "qwen-image")
    ):
        return ModelTypeConst.TTI
    if any(k in model_id for k in ("t2v", "i2v", "video", "sora")):
        return (
            ModelTypeConst.TTV
            if ("t2v" in model_id or "video" in model_id or "sora" in model_id)
            else ModelTypeConst.ITV
        )
    return ModelTypeConst.LLM


class IModelProvider(ABC):
    @abstractmethod
    def get_model_info_manage(self):
        pass

    @abstractmethod
    def get_model_provide_info(self):
        pass

    def get_model_type_list(self):
        return self.get_model_info_manage().get_model_type_list()

    def get_model_list(self, model_type, api_key=None, api_base=None, credential=None):
        if model_type is None:
            raise AppApiException(500, _("Model type cannot be empty"))
        if api_key or credential:
            manage = self._get_dynamic_manage_cached(api_key, api_base, credential)
            if manage is not None:
                return manage.get_model_list_by_model_type(model_type)
        return self.get_model_info_manage().get_model_list_by_model_type(model_type)

    # ---------- 动态模型列表框架 ----------
    # 约定：供应商未提供 api_key 时使用内置 model_info_list；
    # 提供了 api_key 时由 get_dynamic_model_info_list 实时查询官方列表，
    # 默认实现按 OpenAI 兼容协议 GET {api_base}/models，供应商可按官方 API 覆写。

    def get_dynamic_model_info_list(self, api_key, api_base, credential=None):
        """返回实时查询得到的 ModelInfo 列表；查询失败或为空时返回 None（回退内置）。"""
        items = self.fetch_dynamic_model_items(api_key, api_base, credential)
        if not items:
            return None
        builtin_manage = self.get_model_info_manage()
        builtin_by_name = {}
        impl_map = {}
        for info in builtin_manage.model_list:
            builtin_by_name.setdefault(info.name, info)
            impl_map.setdefault(info.model_type, (info.model_credential, info.model_class))
        info_list = []
        for item in items:
            model_id = item.get("id") if isinstance(item, dict) else item
            if not model_id:
                continue
            # 内置列表中已有的模型：类型与实现直接沿用原有逻辑，不依赖关键词猜型。
            builtin = builtin_by_name.get(model_id)
            if builtin is not None:
                info_list.append(
                    ModelInfo(model_id, builtin.desc, builtin.model_type, builtin.model_credential, builtin.model_class)
                )
                continue
            if isinstance(item, dict):
                model_type = self.classify_dynamic_item(item)
            else:
                model_type = self.classify_dynamic_model(model_id)
            impl = impl_map.get(_model_type_name(model_type))
            if impl is None:
                # 视觉输入的对话模型（IMAGE 类型）在无视觉实现时按 LLM 兜底；其余未支持类型直接丢弃。
                if isinstance(model_type, ModelTypeConst) and model_type is ModelTypeConst.IMAGE:
                    impl = impl_map.get("LLM")
                    if impl is not None:
                        model_type = ModelTypeConst.LLM
                if impl is None:
                    continue
            info_list.append(ModelInfo(model_id, _(""), model_type, impl[0], impl[1]))
        return info_list or None

    def classify_dynamic_item(self, item):
        """优先使用 /models 返回的结构化元数据（input/output_modalities 等）判型。"""
        model_id = str(item.get("id") or "")
        input_modalities = {str(m).lower() for m in (item.get("input_modalities") or [])}
        output_modalities = {str(m).lower() for m in (item.get("output_modalities") or [])}
        if "image" in output_modalities:
            return ModelTypeConst.TTI
        if "audio" in output_modalities:
            return ModelTypeConst.TTS
        if "audio" in input_modalities:
            return ModelTypeConst.STT
        if "image" in input_modalities:
            return ModelTypeConst.IMAGE
        return self.classify_dynamic_model(model_id)

    def fetch_dynamic_model_items(self, api_key, api_base, credential=None):
        """OpenAI 兼容协议实时获取模型条目（保留官方元数据，供判型使用）。"""
        api_base = (
            (api_base or self._credential_api_base(credential) or self.get_dynamic_default_api_base() or "")
            .strip()
            .rstrip("/")
        )
        if not api_base:
            return []
        if not api_base.lower().startswith(("http://", "https://")):
            # 仅允许 http/https，防止用户填入 file:/ftp: 等协议被服务端请求。
            return []
        candidates = [api_base + "/models"]
        if "/v1" not in api_base and "/compatible-mode/" not in api_base:
            candidates.insert(0, api_base + "/v1/models")
        for url in candidates:
            try:
                response = requests.get(url, headers={"Authorization": f"Bearer {api_key}"}, timeout=15)
                if response.status_code != 200:
                    continue
                data = response.json()
                items = data.get("data") if isinstance(data, dict) else data
                if isinstance(items, dict):
                    items = items.get("models") or []
                result = []
                seen = set()
                for item in items or []:
                    model_id = item.get("id") if isinstance(item, dict) else item
                    if model_id and model_id not in seen:
                        seen.add(model_id)
                        result.append(item if isinstance(item, dict) else {"id": item})
                if result:
                    return result
            except Exception:
                continue
        return []

    def fetch_dynamic_model_ids(self, api_key, api_base, credential=None):
        """OpenAI 兼容协议实时获取模型 id 列表。"""
        return [item.get("id") for item in self.fetch_dynamic_model_items(api_key, api_base, credential)]

    @staticmethod
    def classify_dynamic_model(model_id):
        return classify_dynamic_model_id(model_id)

    # 供应商可覆盖：未在表单填写 API 地址时的默认列表查询地址。
    dynamic_default_api_base = None

    def get_dynamic_default_api_base(self):
        """从内置凭证表单的 api_base 默认值推断该供应商的默认 API 地址。"""
        cached = getattr(self, "_dynamic_default_api_base", None)
        if cached is not None:
            return cached
        if self.dynamic_default_api_base:
            self._dynamic_default_api_base = self.dynamic_default_api_base
            return self.dynamic_default_api_base
        default = None
        for info in self.get_model_info_manage().model_list:
            try:
                default_data = info.model_credential.get_default_form_data()
            except Exception:
                continue
            value = str(default_data.get("api_base") or "").strip()
            if value:
                default = value
                break
        self._dynamic_default_api_base = default
        return default

    @staticmethod
    def _credential_api_base(credential):
        """从完整凭证里找 API 地址字段（各供应商字段名不同：api_base/base_url 等）。"""
        if not isinstance(credential, dict):
            return None
        for key in ("api_base", "base_url", "api_domain", "domain"):
            value = str(credential.get(key) or "").strip()
            if value:
                return value
        return None

    @staticmethod
    def _credential_cache_fingerprint(credential):
        """完整凭证的缓存指纹：仅取字符串值参与排序，避免大对象。"""
        if not isinstance(credential, dict):
            return ""
        return json.dumps(
            {k: str(v) for k, v in credential.items() if isinstance(v, (str, int, float))}, sort_keys=True
        )

    def _get_dynamic_manage_cached(self, api_key, api_base, credential=None):
        provider = self.get_model_provide_info().provider
        now = time.monotonic()
        cache_key = (provider, api_key, api_base, self._credential_cache_fingerprint(credential))
        cached, cached_at = _dynamic_model_manage_cache.get(cache_key, (None, 0.0))
        if cached is not None and now - cached_at < _DYNAMIC_MODEL_TTL_SECONDS:
            return cached
        failed_at = _dynamic_model_failed_cache.get(cache_key, 0.0)
        if now - failed_at < _DYNAMIC_MODEL_FAILED_TTL_SECONDS:
            return None
        info_list = self.get_dynamic_model_info_list(api_key, api_base, credential)
        if not info_list:
            _dynamic_model_failed_cache[cache_key] = now
            _evict_cache(_dynamic_model_failed_cache, _DYNAMIC_MODEL_FAILED_CACHE_MAX_SIZE)
            return None
        builder = ModelInfoManage.builder()
        for info in info_list:
            builder.append_model_info(info)
        for default in self.get_model_info_manage().default_model_list:
            builder.append_default_model_info(default)
        manage = builder.build()
        _dynamic_model_manage_cache[cache_key] = (manage, now)
        _evict_cache(_dynamic_model_manage_cache, _DYNAMIC_MODEL_CACHE_MAX_SIZE)
        return manage

    def get_model_credential(self, model_type, model_name):
        model_info = self.get_model_info_manage().get_model_info(model_type, model_name)
        model_credential = model_info.model_credential

        if model_type == "TTI" and model_name.startswith(("qwen", "wan2.6", "wan")):
            if hasattr(model_credential, "api_base"):
                api_base = model_credential.api_base
                if hasattr(api_base, "default_value") and not api_base.default_value:
                    api_base.default_value = "https://dashscope.aliyuncs.com/api/v1"
        # MiniMax H3 视频模型固定走 v2 API
        if model_type in ("TTV", "ITV") and model_name.upper().startswith(("MiniMax-H3")):
            if hasattr(model_credential, "api_base"):
                api_base = model_credential.api_base
                if hasattr(api_base, "default_value"):
                    api_base.default_value = "https://api.minimaxi.com/v2"
        return model_credential

    def get_model_params(self, model_type, model_name):
        model_info = self.get_model_info_manage().get_model_info(model_type, model_name)
        return model_info.model_credential

    def is_valid_credential(
        self,
        model_type,
        model_name,
        model_credential: Dict[str, object],
        model_params: Dict[str, object],
        raise_exception=False,
    ):
        model_info = self.get_model_info_manage().get_model_info(model_type, model_name)
        return model_info.model_credential.is_valid(
            model_type, model_name, model_credential, model_params, self, raise_exception=raise_exception
        )

    def get_model(self, model_type, model_name, model_credential: Dict[str, object], **model_kwargs) -> BaseModel:
        model_info = self.get_model_info_manage().get_model_info(model_type, model_name)
        return model_info.model_class.new_instance(model_type, model_name, model_credential, **model_kwargs)

    def get_dialogue_number(self):
        return 3

    def down_model(self, model_type: str, model_name, model_credential: Dict[str, object]) -> Iterator[DownModelChunk]:
        raise AppApiException(500, _("The current platform does not support downloading models"))


class MaxKBBaseModel(ABC):
    @staticmethod
    @abstractmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        pass

    @staticmethod
    def is_cache_model():
        return True

    @staticmethod
    def filter_optional_params(model_kwargs):
        optional_params = {}
        for key, value in model_kwargs.items():
            if key not in ["model_id", "use_local", "streaming", "show_ref_label", "stream"]:
                optional_params[key] = value
        return optional_params


class MaxKBBaseEmbeddingModel(MaxKBBaseModel):
    """All embedding providers must explicitly declare whether they share a text/image vector space."""

    @abstractmethod
    def supports_image_embedding(self) -> bool:
        """Return True only when image and text embeddings are comparable in the same vector space."""
        pass

    def embed_images(self, images: List[str]) -> List[List[float]]:
        """Embed data URLs or provider-supported image URLs."""
        raise AppApiException(500, _("The current embedding model does not support image embedding"))

    @staticmethod
    def normalize_image_input(url: str, keep_data_prefix: bool = False) -> str:
        """归一化图片输入为上游接口可识别的字符串。

        - http(s) URL：原样返回
        - data:image/...;base64,xxx：keep_data_prefix=True 保留 data URI（阿里百炼等），
          False 只返回 base64 内容（腾讯 TokenHub 等）
        - 其它字符串：视为已是目标格式，原样返回
        """
        if url.startswith(("http://", "https://")):
            return url
        if url.startswith("data:") and ";base64," in url:
            if keep_data_prefix:
                return url
            return url.split(";base64,", 1)[1]
        return url


class BaseModelCredential(ABC):
    @abstractmethod
    def is_valid(
        self, model_type: str, model_name, model: Dict[str, object], model_params, provider, raise_exception=True
    ):
        pass

    @abstractmethod
    def encryption_dict(self, model_info: Dict[str, object]):
        """
        :param model_info: 模型数据
        :return: 加密后数据
        """
        pass

    def get_model_params_setting_form(self, model_name):
        """
        模型参数设置表单
        :return:
        """
        pass

    @staticmethod
    def encryption(message: str):
        """
            加密敏感字段数据  加密方式是 如果密码是 1234567890  那么给前端则是 123******890
        :param message:
        :return:
        """
        return encryption(message)


class ModelTypeConst(Enum):
    LLM = {"code": "LLM", "message": _("LLM")}
    EMBEDDING = {"code": "EMBEDDING", "message": _("Embedding Model")}
    STT = {"code": "STT", "message": _("Speech2Text")}
    TTS = {"code": "TTS", "message": _("TTS")}
    IMAGE = {"code": "IMAGE", "message": _("Vision Model")}
    TTI = {"code": "TTI", "message": _("Image Generation")}
    RERANKER = {"code": "RERANKER", "message": _("Rerank")}
    # 文生视频 图生视频
    TTV = {"code": "TTV", "message": _("Text to Video")}
    ITV = {"code": "ITV", "message": _("Image to Video")}


class ModelInfo:
    def __init__(
        self,
        name: str,
        desc: str,
        model_type: ModelTypeConst,
        model_credential: BaseModelCredential,
        model_class: Type[MaxKBBaseModel],
        **keywords,
    ):
        self.name = name
        self.desc = desc
        self.model_type = model_type.name if isinstance(model_type, ModelTypeConst) else str(model_type)
        self.model_credential = model_credential
        self.model_class = model_class
        if keywords is not None:
            for key in keywords.keys():
                self.__setattr__(key, keywords.get(key))

    def get_name(self):
        """
        获取模型名称
        :return: 模型名称
        """
        return self.name

    def get_desc(self):
        """
        获取模型描述
        :return: 模型描述
        """
        return self.desc

    def get_model_type(self):
        return self.model_type

    def get_model_class(self):
        return self.model_class

    def to_dict(self):
        return reduce(
            lambda x, y: {**x, **y},
            [
                {attr: self.__getattribute__(attr)}
                for attr in vars(self)
                if not attr.startswith("__") and not attr == "model_credential" and not attr == "model_class"
            ],
            {},
        )


class ModelInfoManage:
    def __init__(self):
        self.model_dict = {}
        self.model_list = []
        self.default_model_list = []
        self.default_model_dict = {}

    def append_model_info(self, model_info: ModelInfo):
        self.model_list.append(model_info)
        model_type_dict = self.model_dict.get(model_info.model_type)
        if model_type_dict is None:
            self.model_dict[model_info.model_type] = {model_info.name: model_info}
        else:
            model_type_dict[model_info.name] = model_info

    def append_default_model_info(self, model_info: ModelInfo):
        self.default_model_list.append(model_info)
        self.default_model_dict[model_info.model_type] = model_info

    def get_model_list(self):
        return [model.to_dict() for model in self.model_list]

    def get_model_list_by_model_type(self, model_type):
        return [model.to_dict() for model in self.model_list if model.model_type == model_type]

    def get_model_type_list(self):
        return [
            {"key": _type.value.get("message"), "value": _type.value.get("code")}
            for _type in ModelTypeConst
            if len([model for model in self.model_list if model.model_type == _type.name]) > 0
        ]

    def get_model_info(self, model_type, model_name) -> ModelInfo:
        model_info = self.model_dict.get(model_type, {}).get(model_name, self.default_model_dict.get(model_type))
        if model_info is None:
            raise AppApiException(500, _("The model does not support"))
        return model_info

    class builder:
        def __init__(self):
            self.modelInfoManage = ModelInfoManage()

        def append_model_info(self, model_info: ModelInfo):
            self.modelInfoManage.append_model_info(model_info)
            return self

        def append_model_info_list(self, model_info_list: List[ModelInfo]):
            for model_info in model_info_list:
                self.modelInfoManage.append_model_info(model_info)
            return self

        def append_default_model_info(self, model_info: ModelInfo):
            self.modelInfoManage.append_default_model_info(model_info)
            return self

        def build(self):
            return self.modelInfoManage


class ModelProvideInfo:
    def __init__(self, provider: str, name: str, icon: str):
        self.provider = provider

        self.name = name

        self.icon = icon

    def to_dict(self):
        return reduce(
            lambda x, y: {**x, **y},
            [{attr: self.__getattribute__(attr)} for attr in vars(self) if not attr.startswith("__")],
            {},
        )
