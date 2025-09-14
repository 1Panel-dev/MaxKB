# coding=utf-8
from abc import abstractmethod

from pydantic import BaseModel


class BaseGenerationVideo(BaseModel):
    @abstractmethod
    def check_auth(self):
        pass

    @abstractmethod
    def generate_video(self, prompt: str, negative_prompt: str = None, first_frame_url=None, last_frame_url=None):
        pass
