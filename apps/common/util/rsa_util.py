# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： rsa_util.py
    @date：2023/11/3 11:13
    @desc:
"""
import base64
import os

from Crypto.Cipher import PKCS1_v1_5 as PKCS1_cipher
from Crypto.PublicKey import RSA

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
    if not os.path.exists("/opt/maxkb/conf/receiver.pem"):
        kv = generate()
        private_file_out = open("/opt/maxkb/conf/private.pem", "wb")
        private_file_out.write(kv.get('value'))
        private_file_out.close()
        receiver_file_out = open("/opt/maxkb/conf/receiver.pem", "wb")
        receiver_file_out.write(kv.get('key'))
        receiver_file_out.close()
    return {'key': open("/opt/maxkb/conf/receiver.pem").read(), 'value': open("/opt/maxkb/conf/private.pem").read()}


def encrypt(msg, public_key: str | None = None):
    """
    加密
    :param msg:        加密数据
    :param public_key: 公钥
    :return: 加密后的数据
    """
    if public_key is None:
        public_key = get_key_pair().get('key')
    cipher = PKCS1_cipher.new(RSA.importKey(public_key))
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
    cipher = PKCS1_cipher.new(RSA.importKey(pri_key, passphrase=secret_code))
    decrypt_data = cipher.decrypt(base64.b64decode(msg), 0)
    return decrypt_data.decode("utf-8")
