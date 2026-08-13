# coding=utf-8
"""
@project: MaxKB
@Author：虎
@file： embedding.py
@date：2024/10/17 15:29
@desc:
"""

import queue
import threading
import time
from typing import Dict, Optional

import base64
import json
import numpy as np
from numpy import ndarray

from models_provider.base_model_provider import MaxKBBaseEmbeddingModel
from models_provider.langchain_compat.sparkllm import SparkLLMTextEmbeddings

_task_queue = queue.Queue()


def _worker():
    while True:
        message, future = _task_queue.get()

        for i in range(3):
            try:
                data = json.loads(message)
                code = data["header"]["code"]

                if code != 0:
                    raise Exception(f"Request error: {code}, {data}")

                text_base = data["payload"]["feature"]["text"]
                text_data = base64.b64decode(text_base)

                dt = np.dtype(np.float32)
                dt = dt.newbyteorder("<")

                text = np.frombuffer(text_data, dtype=dt)

                if len(text) > 2560:
                    array = text[:2560]
                else:
                    array = text

                future["result"] = array
                future["event"].set()
                break

            except Exception as e:
                if i == 2:
                    future["error"] = e
                    future["event"].set()
                else:
                    time.sleep(0.5)

        time.sleep(0.5)  # QPS=2


threading.Thread(target=_worker, daemon=True).start()


class XFEmbedding(MaxKBBaseEmbeddingModel, SparkLLMTextEmbeddings):
    def supports_image_embedding(self) -> bool:
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        return XFEmbedding(
            base_url=model_credential.get("base_url"),
            spark_app_id=model_credential.get("spark_app_id"),
            spark_api_key=model_credential.get("spark_api_key"),
            spark_api_secret=model_credential.get("spark_api_secret"),
        )

    @staticmethod
    def _parser_message(
        message: str,
    ) -> Optional[ndarray]:
        future = {"event": threading.Event(), "result": None, "error": None}

        _task_queue.put((message, future))

        future["event"].wait()

        if future["error"]:
            raise future["error"]

        return future["result"]
