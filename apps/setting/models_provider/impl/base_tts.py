# coding=utf-8
from abc import abstractmethod

from pydantic import BaseModel


class BaseTextToSpeech(BaseModel):
    @abstractmethod
    def check_auth(self):
        pass

    @abstractmethod
    def text_to_speech(self, text):
        pass
