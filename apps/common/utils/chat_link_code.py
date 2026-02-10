"""
    @project: MaxKB
    @Author: niu
    @file: chat_link_code.py
    @date: 2026/2/9 11:31
    @desc:
"""
from typing import Union

import uuid_utils.compat as uuid


class UUIDEncoder:

    BASE62_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    BASE62_LEN = 62

    @staticmethod
    def encode(uuid_obj: Union[uuid.UUID, str] = None) -> str:

        if uuid_obj is None:
            uuid_obj = uuid.uuid7()
        elif isinstance(uuid_obj, str):
            uuid_obj = uuid.UUID(uuid_obj)

        num = int(uuid_obj.hex, 16)

        if num == 0:
            return UUIDEncoder.BASE62_ALPHABET[0]

        result = []
        while num:
            num, rem = divmod(num,62)
            result.append(UUIDEncoder.BASE62_ALPHABET[rem])
        return ''.join(reversed(result))

    @staticmethod
    def decode(encoded: str) -> uuid.UUID:

        num = 0
        for char in encoded:
            num = num * UUIDEncoder.BASE62_LEN + UUIDEncoder.BASE62_ALPHABET.index(char)

        return uuid.UUID(int=num)

    @staticmethod
    def decode_to_str(encoded: str) -> str:
        return str(UUIDEncoder.decode(encoded))