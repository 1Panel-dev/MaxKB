import base64
import os
import traceback
from typing import Dict

from openai import OpenAI

from common.utils.logger import maxkb_logger
from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_stt import BaseSpeechToText


class AliyunBaiLianOmiSpeechToText(MaxKBBaseModel, BaseSpeechToText):
    api_key: str
    api_url: str
    model: str
    params: dict

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get('api_key')
        self.model = kwargs.get('model')
        self.params = kwargs.get('params')
        self.api_url = kwargs.get('api_url')

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        return AliyunBaiLianOmiSpeechToText(
            model=model_name,
            api_key=model_credential.get('api_key'),
            api_url=model_credential.get('api_url') ,
            params= model_kwargs,
            **model_kwargs
        )


    def check_auth(self):
        cwd = os.path.dirname(os.path.abspath(__file__))
        with open(f'{cwd}/iat_mp3_16k.mp3', 'rb') as audio_file:
            self.speech_to_text(audio_file)



    def speech_to_text(self, audio_file):
        try:
            client = OpenAI(
                # 若没有配置环境变量，请用阿里云百炼API Key将下行替换为：api_key="sk-xxx",
                api_key=self.api_key,
                base_url=self.api_url,
            )

            base64_audio = base64.b64encode(audio_file.read()).decode("utf-8")

            completion = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_audio",
                                "input_audio": {
                                    "data": f"data:;base64,{base64_audio}",
                                    "format": "mp3",
                                },
                            },
                            {"type": "text", "text": self.params.get('CueWord')},
                        ],
                    },
                ],
                # 设置输出数据的模态，当前支持两种：["text","audio"]、["text"]
                modalities=["text"],
                # stream 必须设置为 True，否则会报错
                stream=True,
                stream_options={"include_usage": True},
            )
            result = []
            for chunk in completion:
                if chunk.choices and hasattr(chunk.choices[0].delta, 'content'):
                    content = chunk.choices[0].delta.content
                    result.append(content)
            return "".join(result)

        except Exception as err:
            maxkb_logger.error(f":Error: {str(err)}: {traceback.format_exc()}")
