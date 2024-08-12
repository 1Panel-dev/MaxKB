# coding=utf-8
import threading
from typing import Dict

from langchain_community.embeddings import XinferenceEmbeddings

from setting.models_provider.base_model_provider import MaxKBBaseModel


class XinferenceEmbedding(MaxKBBaseModel, XinferenceEmbeddings):
    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        return XinferenceEmbedding(
            model_uid=model_name,
            server_url=model_credential.get('api_base'),
        )

    def down_model(self):
        self.client.launch_model(model_name=self.model_uid, model_type="embedding")

    def start_down_model_thread(self):
        thread = threading.Thread(target=self.down_model)
        thread.daemon = True
        thread.start()
