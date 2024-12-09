# coding=utf-8
from abc import abstractmethod

from pydantic import BaseModel


class BaseTextToImage(BaseModel):
    @abstractmethod
    def check_auth(self):
        pass

    @abstractmethod
    def generate_image(self, prompt: str, negative_prompt: str = None):
        pass
