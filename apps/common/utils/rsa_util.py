# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： rsa_util.py
    @date：2023/11/3 11:13
    @desc:
"""
import base64
import threading
from functools import lru_cache

from Crypto.Cipher import PKCS1_v1_5 as PKCS1_cipher
from Crypto.PublicKey import RSA
from django.core import cache
from django.db.models import QuerySet

from common.constants.cache_version import Cache_Version
from system_manage.models import SystemSetting, SettingType

lock = threading.Lock()
rsa_cache = cache.cache
cache_key = "rsa_key"
# 对密钥加密的密码
secret_code = "mac_kb_password"


def generate():
    """
    生成 私钥秘钥对
    :return:{key:'公钥',value:'私钥'}
    """
    # 生成一个 2048 位的密钥
    key = RSA.generate(2048)

    # 获取私钥
    encrypted_key = key.export_key(passphrase=secret_code, pkcs=8,
                                   protection="scryptAndAES128-CBC")
    return {'key': key.publickey().export_key(), 'value': encrypted_key}


def get_key_pair():
    rsa_value = rsa_cache.get(cache_key)
    if rsa_value is None:
        with lock:
            rsa_value = rsa_cache.get(cache_key)
            if rsa_value is not None:
                return rsa_value
            rsa_value = get_key_pair_by_sql()
            version, get_key = Cache_Version.SYSTEM.value
            rsa_cache.set(get_key(key='rsa_key'), rsa_value, timeout=None, version=version)
    return rsa_value


def get_key_pair_by_sql():
    system_setting = QuerySet(SystemSetting).filter(type=SettingType.RSA.value).first()
    if system_setting is None:
        kv = generate()
        system_setting = SystemSetting(type=SettingType.RSA.value,
                                       meta={'key': kv.get('key').decode(), 'value': kv.get('value').decode()})
        system_setting.save()
    return system_setting.meta


def encrypt(msg, public_key: str | None = None):
    """
    加密
    :param msg:        加密数据
    :param public_key: 公钥
    :return: 加密后的数据
    """
    if public_key is None:
        public_key = get_key_pair().get('key')
    cipher = _get_encrypt_cipher(public_key)
    encrypt_msg = cipher.encrypt(msg.encode("utf-8"))
    return base64.b64encode(encrypt_msg).decode()


def decrypt(msg, pri_key: str | None = None):
    """
    解密
    :param msg: 需要解密的数据
    :param pri_key: 私钥
    :return: 解密后数据
    """
    if pri_key is None:
        pri_key = get_key_pair().get('value')
    cipher = _get_cipher(pri_key)
    decrypt_data = cipher.decrypt(base64.b64decode(msg), 0)
    return decrypt_data.decode("utf-8")



@lru_cache(maxsize=2)
def _get_encrypt_cipher(public_key: str):
    """缓存加密 cipher 对象"""
    return PKCS1_cipher.new(RSA.importKey(extern_key=public_key, passphrase=secret_code))


def rsa_long_encrypt(message, public_key: str | None = None, length=200):
    """
    超长文本加密

    :param message:         需要加密的字符串
    :param public_key   公钥
    :param length:      1024bit的证书用100, 2048bit的证书用 200
    :return: 加密后的数据
    """
    if public_key is None:
        public_key = get_key_pair().get('key')

    cipher = _get_encrypt_cipher(public_key)

    if len(message) <= length:
        result = base64.b64encode(cipher.encrypt(message.encode('utf-8')))
    else:
        rsa_text = []
        for i in range(0, len(message), length):
            cont = message[i:i + length]
            rsa_text.append(cipher.encrypt(cont.encode('utf-8')))
        cipher_text = b''.join(rsa_text)
        result = base64.b64encode(cipher_text)

    return result.decode()


@lru_cache(maxsize=2)
def _get_cipher(pri_key: str):
    """缓存 cipher 对象,避免重复创建"""
    return PKCS1_cipher.new(RSA.importKey(pri_key, passphrase=secret_code))


def rsa_long_decrypt(message, pri_key: str | None = None, length=256):
    """
    超长文本解密,优化内存使用
    :param  message:    需要解密的数据
    :param  pri_key:    秘钥
    :param  length :     1024bit的证书用128,2048bit证书用256位
    :return: 解密后的数据
    """
    if pri_key is None:
        pri_key = get_key_pair().get('value')

    cipher = _get_cipher(pri_key)
    base64_de = base64.b64decode(message)

    # 使用 bytearray 减少内存分配
    result = bytearray()
    for i in range(0, len(base64_de), length):
        result.extend(cipher.decrypt(base64_de[i:i + length], 0))

    return result.decode()

