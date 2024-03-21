# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： test.py
    @date：2023/11/15 15:13
    @desc:
"""
import hashlib
import time

from django.core import signing
from django.core.cache import cache

# alg使用的算法
HEADER = {'typ': 'JWP', 'alg': 'default'}
TOKEN_KEY = 'solomon_world_token'
TOKEN_SALT = 'solomonwanc@gmail.com'
TIME_OUT = 30 * 60

# 加密
def encrypt(obj):
    value = signing.dumps(obj, key=TOKEN_KEY, salt=TOKEN_SALT)
    value = signing.b64_encode(value.encode()).decode()
    return value


# 解密
def decrypt(src):
    src = signing.b64_decode(src.encode()).decode()
    raw = signing.loads(src, key=TOKEN_KEY, salt=TOKEN_SALT)
    print(type(raw))
    return raw


# 生成token信息
def create_token(username, password):
    # 1. 加密头信息
    header = encrypt(HEADER)
    # 2. 构造Payload
    payload = {
        "username": username,
        "password": password,
        "iat": time.time()
    }
    payload = encrypt(payload)
    # 3. 生成签名
    md5 = hashlib.md5()
    md5.update(("%s.%s" % (header, payload)).encode())
    signature = md5.hexdigest()
    token = "%s.%s.%s" % (header, payload, signature)
    # 4.存储到缓存中
    cache.set(username, token, TIME_OUT)
    return token


def get_payload(token):
    payload = str(token).split('.')[1]
    payload = decrypt(payload)
    return payload


# 通过token获取用户名
def get_username(token):
    payload = get_payload(token)
    return payload['username']
    pass


def check_token(token):
    username = get_username(token)
    print('username', username)
    last_token = cache.get(username)
    if last_token:
        return last_token == token
    return False


