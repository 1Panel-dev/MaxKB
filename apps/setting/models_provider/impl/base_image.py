# coding=utf-8
from abc import abstractmethod

from pydantic import BaseModel


class BaseImage(BaseModel):
    @abstractmethod
    def check_auth(self):
        pass

    @abstractmethod
    def image_understand(self, image_file, text):
        pass
