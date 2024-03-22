# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： base_model_provider.py
    @date：2023/10/31 16:19
    @desc:
"""
from abc import ABC, abstractmethod
from enum import Enum
from functools import reduce
from typing import Dict, Iterator

from langchain.chat_models.base import BaseChatModel

from common.exception.app_exception import AppApiException


class DownModelChunkStatus(Enum):
    success = "success"
    error = "error"
    pulling = "pulling"
    unknown = 'unknown'


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
            "index": self.index
        }


class IModelProvider(ABC):

    @abstractmethod
    def get_model_provide_info(self):
        pass

    @abstractmethod
    def get_model_type_list(self):
        pass

    @abstractmethod
    def get_model_list(self, model_type):
        pass

    @abstractmethod
    def get_model_credential(self, model_type, model_name):
        pass

    @abstractmethod
    def get_model(self, model_type, model_name, model_credential: Dict[str, object], **model_kwargs) -> BaseChatModel:
        pass

    @abstractmethod
    def get_dialogue_number(self):
        pass

    def down_model(self, model_type: str, model_name, model_credential: Dict[str, object]) -> Iterator[DownModelChunk]:
        raise AppApiException(500, "当前平台不支持下载模型")


class BaseModelCredential(ABC):

    @abstractmethod
    def is_valid(self, model_type: str, model_name, model: Dict[str, object], raise_exception=False):
        pass

    @abstractmethod
    def encryption_dict(self, model_info: Dict[str, object]):
        """
        :param model_info: 模型数据
        :return: 加密后数据
        """
        pass

    @staticmethod
    def encryption(message: str):
        """
            加密敏感字段数据  加密方式是 如果密码是 1234567890  那么给前端则是 123******890
        :param message:
        :return:
        """
        max_pre_len = 8
        max_post_len = 4
        message_len = len(message)
        pre_len = int(message_len / 5 * 2)
        post_len = int(message_len / 5 * 1)
        pre_str = "".join([message[index] for index in
                           range(0, max_pre_len if pre_len > max_pre_len else 1 if pre_len <= 0 else int(pre_len))])
        end_str = "".join(
            [message[index] for index in
             range(message_len - (int(post_len) if pre_len < max_post_len else max_post_len), message_len)])
        content = "***************"
        return pre_str + content + end_str


class ModelTypeConst(Enum):
    LLM = {'code': 'LLM', 'message': '大语言模型'}


class ModelInfo:
    def __init__(self, name: str, desc: str, model_type: ModelTypeConst, model_credential: BaseModelCredential,
                 **keywords):
        self.name = name
        self.desc = desc
        self.model_type = model_type.name
        self.model_credential = model_credential
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

    def to_dict(self):
        return reduce(lambda x, y: {**x, **y},
                      [{attr: self.__getattribute__(attr)} for attr in vars(self) if
                       not attr.startswith("__") and not attr == 'model_credential'], {})


class ModelProvideInfo:
    def __init__(self, provider: str, name: str, icon: str):
        self.provider = provider

        self.name = name

        self.icon = icon

    def to_dict(self):
        return reduce(lambda x, y: {**x, **y},
                      [{attr: self.__getattribute__(attr)} for attr in vars(self) if
                       not attr.startswith("__")], {})
