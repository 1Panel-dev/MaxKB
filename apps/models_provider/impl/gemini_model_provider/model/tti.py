import base64
from typing import Dict

from openai import OpenAI

from common.config.tokenizer_manage_config import TokenizerManage
from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_tti import BaseTextToImage


def custom_get_token_ids(text: str):
    tokenizer = TokenizerManage.get_tokenizer()
    return tokenizer.encode(text)


class GeminiTextToImage(MaxKBBaseModel, BaseTextToImage):
    base_url: str
    api_key: str
    model: str
    params: dict

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get('api_key')
        self.base_url = kwargs.get('base_url')
        self.model = kwargs.get('model')
        self.params = kwargs.get('params')

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {'params': {}}
        for key, value in model_kwargs.items():
            if key not in ['model_id', 'use_local', 'streaming']:
                optional_params['params'][key] = value
        return GeminiTextToImage(
            model=model_name,
            base_url=model_credential.get('base_url', "https://generativelanguage.googleapis.com"),
            api_key=model_credential.get('api_key'),
            **optional_params,
        )

    def check_auth(self):
        return True

    def generate_image(self, prompt: str, negative_prompt: str = None):
        from google import genai
        from google.genai import types
        from PIL import Image
        file_urls = []
        client = genai.Client(api_key=self.api_key, http_options={"base_url": self.base_url}, **self.params)
        if self.model.startswith('imagen'):
            config = types.GenerateImagesConfig(**self.params)

            # 如果有 negative_prompt 就加入
            if negative_prompt:
                config.negative_prompt = negative_prompt
            response = client.models.generate_images(
                model=self.model,
                prompt=prompt,
                config=config
            )
            for generated_image in response.generated_images:
                img_base64 = base64.b64encode(generated_image.image.image_bytes).decode("utf-8")
                file_urls.append(f'data:{generated_image.image.mime_type};base64,{img_base64}')
        else:
            config = types.GenerateContentConfig(**self.params)
            if negative_prompt:
                config.negative_prompt = negative_prompt
            response = client.models.generate_content(
                model=self.model,
                contents=[prompt],
                config=config
            )

            for part in response.parts:
                if part.text is not None:
                    print(part.text)
                elif part.inline_data is not None:
                    image_bytes = part.inline_data.data
                    img_base64 = base64.b64encode(image_bytes).decode("utf-8")
                    file_urls.append(f'data:{part.inline_data.mime_type};base64,{img_base64}')

        return file_urls
