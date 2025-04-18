# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： tokenizer_manage_config.py
    @date：2024/4/28 10:17
    @desc:
"""


class TokenizerManage:
    tokenizer = None

    @staticmethod
    def get_tokenizer():
        from transformers import BertTokenizer
        if TokenizerManage.tokenizer is None:
            TokenizerManage.tokenizer = BertTokenizer.from_pretrained(
                'bert-base-cased',
                cache_dir="/opt/maxkb-app/model/tokenizer",
                local_files_only=True,
                resume_download=False,
                force_download=False)
        return TokenizerManage.tokenizer
