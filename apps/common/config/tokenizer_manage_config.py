# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： tokenizer_manage_config.py
    @date：2024/4/28 10:17
    @desc:
"""

import os

class MKTokenizer:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    def encode(self, text):
        return self.tokenizer.encode(text).ids


class TokenizerManage:
    tokenizer = None

    @staticmethod
    def get_tokenizer():
        from tokenizers import Tokenizer
        # 创建Tokenizer
        model_path = os.path.join("/opt/maxkb-app", "model", "tokenizer", "models--bert-base-cased")
        with open(f"{model_path}/refs/main", encoding="utf-8") as f: snapshot = f.read()
        TokenizerManage.tokenizer = Tokenizer.from_file(f"{model_path}/snapshots/{snapshot}/tokenizer.json")
        return MKTokenizer(TokenizerManage.tokenizer)
