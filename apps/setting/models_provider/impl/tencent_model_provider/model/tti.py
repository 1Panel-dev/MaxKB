# coding=utf-8

import json
from typing import Dict

from django.utils.translation import gettext as _
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.hunyuan.v20230901 import hunyuan_client, models

from setting.models_provider.base_model_provider import MaxKBBaseModel
from setting.models_provider.impl.base_tti import BaseTextToImage
from setting.models_provider.impl.tencent_model_provider.model.hunyuan import ChatHunyuan


class TencentTextToImageModel(MaxKBBaseModel, BaseTextToImage):
    hunyuan_secret_id: str
    hunyuan_secret_key: str
    model: str
    params: dict

    @staticmethod
    def is_cache_model():
        return False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hunyuan_secret_id = kwargs.get('hunyuan_secret_id')
        self.hunyuan_secret_key = kwargs.get('hunyuan_secret_key')
        self.model = kwargs.get('model_name')
        self.params = kwargs.get('params')

    @staticmethod
    def new_instance(model_type: str, model_name: str, model_credential: Dict[str, object],
                     **model_kwargs) -> 'TencentTextToImageModel':
        optional_params = {'params': {'Style': '201', 'Resolution': '768:768'}}
        for key, value in model_kwargs.items():
            if key not in ['model_id', 'use_local', 'streaming']:
                optional_params['params'][key] = value
        return TencentTextToImageModel(
            model=model_name,
            hunyuan_secret_id=model_credential.get('hunyuan_secret_id'),
            hunyuan_secret_key=model_credential.get('hunyuan_secret_key'),
            **optional_params
        )

    def check_auth(self):
        chat = ChatHunyuan(hunyuan_app_id='111111',
                           hunyuan_secret_id=self.hunyuan_secret_id,
                           hunyuan_secret_key=self.hunyuan_secret_key,
                           model="hunyuan-standard")
        res = chat.invoke(_('Hello'))
        # print(res)

    def generate_image(self, prompt: str, negative_prompt: str = None):
        try:
            # 实例化一个认证对象，入参需要传入腾讯云账户 SecretId 和 SecretKey，此处还需注意密钥对的保密
            # 代码泄露可能会导致 SecretId 和 SecretKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考，建议采用更安全的方式来使用密钥，请参见：https://cloud.tencent.com/document/product/1278/85305
            # 密钥可前往官网控制台 https://console.cloud.tencent.com/cam/capi 进行获取
            cred = credential.Credential(self.hunyuan_secret_id, self.hunyuan_secret_key)
            # 实例化一个http选项，可选的，没有特殊需求可以跳过
            httpProfile = HttpProfile()
            httpProfile.endpoint = "hunyuan.tencentcloudapi.com"

            # 实例化一个client选项，可选的，没有特殊需求可以跳过
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            # 实例化要请求产品的client对象,clientProfile是可选的
            client = hunyuan_client.HunyuanClient(cred, "ap-guangzhou", clientProfile)

            # 实例化一个请求对象,每个接口都会对应一个request对象
            req = models.TextToImageLiteRequest()
            params = {
                "Prompt": prompt,
                "NegativePrompt": negative_prompt,
                "RspImgType": "url",
                **self.params
            }
            req.from_json_string(json.dumps(params))

            # 返回的resp是一个TextToImageLiteResponse的实例，与请求对象对应
            resp = client.TextToImageLite(req)
            # 输出json格式的字符串回包
            print(resp.to_json_string())
            file_urls = []

            file_urls.append(resp.ResultImage)
            return file_urls
        except TencentCloudSDKException as err:
            print(err)
