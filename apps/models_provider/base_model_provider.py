# coding=utf-8

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


class IModelProvider(ABC):
    @abstractmethod
    def get_model_info_manage(self):
        pass

    @abstractmethod
    def get_model_provide_info(self):
        pass

    def get_model_type_list(self):
        return self.get_model_info_manage().get_model_type_list()

    def get_model_list(self, model_type):
        if model_type is None:
            raise AppApiException(500, _("Model type cannot be empty"))
        return self.get_model_info_manage().get_model_list_by_model_type(model_type)

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
        self.model_type = model_type.name
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
