# coding=utf-8
from abc import abstractmethod

from pydantic import BaseModel


class BaseSpeechToText(BaseModel):
    @abstractmethod
    def check_auth(self):
        pass

    @abstractmethod
    def speech_to_text(self, audio_file):
        pass
