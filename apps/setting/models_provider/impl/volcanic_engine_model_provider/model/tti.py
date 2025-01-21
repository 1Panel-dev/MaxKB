# coding=utf-8

'''
requires Python 3.6 or later

pip install asyncio
pip install websockets

'''

import datetime
import hashlib
import hmac
import json
import sys
from typing import Dict

import requests

from setting.models_provider.base_model_provider import MaxKBBaseModel
from setting.models_provider.impl.base_tti import BaseTextToImage

method = 'POST'
host = 'visual.volcengineapi.com'
region = 'cn-north-1'
endpoint = 'https://visual.volcengineapi.com'
service = 'cv'

req_key_dict = {
    'general_v1.4': 'high_aes_general_v14',
    'general_v2.0': 'high_aes_general_v20',
    'general_v2.0_L': 'high_aes_general_v20_L',
    'anime_v1.3': 'high_aes',
    'anime_v1.3.1': 'high_aes',
}


def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()


def getSignatureKey(key, dateStamp, regionName, serviceName):
    kDate = sign(key.encode('utf-8'), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'request')
    return kSigning


def formatQuery(parameters):
    request_parameters_init = ''
    for key in sorted(parameters):
        request_parameters_init += key + '=' + parameters[key] + '&'
    request_parameters = request_parameters_init[:-1]
    return request_parameters


def signV4Request(access_key, secret_key, service, req_query, req_body):
    if access_key is None or secret_key is None:
        print('No access key is available.')
        sys.exit()

    t = datetime.datetime.utcnow()
    current_date = t.strftime('%Y%m%dT%H%M%SZ')
    # current_date = '20210818T095729Z'
    datestamp = t.strftime('%Y%m%d')  # Date w/o time, used in credential scope
    canonical_uri = '/'
    canonical_querystring = req_query
    signed_headers = 'content-type;host;x-content-sha256;x-date'
    payload_hash = hashlib.sha256(req_body.encode('utf-8')).hexdigest()
    content_type = 'application/json'
    canonical_headers = 'content-type:' + content_type + '\n' + 'host:' + host + \
                        '\n' + 'x-content-sha256:' + payload_hash + \
                        '\n' + 'x-date:' + current_date + '\n'
    canonical_request = method + '\n' + canonical_uri + '\n' + canonical_querystring + \
                        '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash
    # print(canonical_request)
    algorithm = 'HMAC-SHA256'
    credential_scope = datestamp + '/' + region + '/' + service + '/' + 'request'
    string_to_sign = algorithm + '\n' + current_date + '\n' + credential_scope + '\n' + hashlib.sha256(
        canonical_request.encode('utf-8')).hexdigest()
    # print(string_to_sign)
    signing_key = getSignatureKey(secret_key, datestamp, region, service)
    # print(signing_key)
    signature = hmac.new(signing_key, (string_to_sign).encode(
        'utf-8'), hashlib.sha256).hexdigest()
    # print(signature)

    authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + \
                           credential_scope + ', ' + 'SignedHeaders=' + \
                           signed_headers + ', ' + 'Signature=' + signature
    # print(authorization_header)
    headers = {'X-Date': current_date,
               'Authorization': authorization_header,
               'X-Content-Sha256': payload_hash,
               'Content-Type': content_type
               }
    # print(headers)

    # ************* SEND THE REQUEST *************
    request_url = endpoint + '?' + canonical_querystring

    print('\nBEGIN REQUEST++++++++++++++++++++++++++++++++++++')
    print('Request URL = ' + request_url)
    try:
        r = requests.post(request_url, headers=headers, data=req_body)
    except Exception as err:
        print(f'error occurred: {err}')
        raise
    else:
        print('\nRESPONSE++++++++++++++++++++++++++++++++++++')
        print(f'Response code: {r.status_code}\n')
        # 使用 replace 方法将 \u0026 替换为 &
        resp_str = r.text.replace("\\u0026", "&")
        if r.status_code != 200:
            raise Exception(f'Error: {resp_str}')
        print(f'Response body: {resp_str}\n')
        return json.loads(resp_str)['data']['image_urls']


class VolcanicEngineTextToImage(MaxKBBaseModel, BaseTextToImage):
    access_key: str
    secret_key: str
    model_version: str
    params: dict

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.access_key = kwargs.get('access_key')
        self.secret_key = kwargs.get('secret_key')
        self.model_version = kwargs.get('model_version')
        self.params = kwargs.get('params')

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {'params': {}}
        for key, value in model_kwargs.items():
            if key not in ['model_id', 'use_local', 'streaming']:
                optional_params['params'][key] = value
        return VolcanicEngineTextToImage(
            model_version=model_name,
            access_key=model_credential.get('access_key'),
            secret_key=model_credential.get('secret_key'),
            **optional_params
        )

    def check_auth(self):
        res = self.generate_image('生成一张小猫图片')
        print(res)

    def generate_image(self, prompt: str, negative_prompt: str = None):
        # 请求Query，按照接口文档中填入即可
        query_params = {
            'Action': 'CVProcess',
            'Version': '2022-08-31',
        }
        formatted_query = formatQuery(query_params)
        size = self.params.pop('size', '512*512').split('*')
        body_params = {
            "req_key": req_key_dict[self.model_version],
            "prompt": prompt,
            "model_version": self.model_version,
            "return_url": True,
            "width": int(size[0]),
            "height": int(size[1]),
            **self.params
        }
        formatted_body = json.dumps(body_params)
        return signV4Request(self.access_key, self.secret_key, service, formatted_query, formatted_body)

    def is_cache_model(self):
        return False
