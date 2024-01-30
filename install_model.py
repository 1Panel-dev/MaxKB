# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： install_model.py
    @date：2023/12/18 14:02
    @desc:
"""
import json
import os.path
from pycrawlers import huggingface
from transformers import GPT2TokenizerFast
hg = huggingface()
prefix_dir = "./model"
model_config = [
    {
        'download_params': {
            'cache_dir': os.path.join(prefix_dir, 'base/hub'),
            'pretrained_model_name_or_path': 'gpt2'
        },
        'download_function': GPT2TokenizerFast.from_pretrained
    },
    {
        'download_params': {
            'cache_dir': os.path.join(prefix_dir, 'base/hub'),
            'pretrained_model_name_or_path': 'gpt2-medium'
        },
        'download_function': GPT2TokenizerFast.from_pretrained
    },
    {
        'download_params': {
            'cache_dir': os.path.join(prefix_dir, 'base/hub'),
            'pretrained_model_name_or_path': 'gpt2-large'
        },
        'download_function': GPT2TokenizerFast.from_pretrained
    },
    {
        'download_params': {
            'cache_dir': os.path.join(prefix_dir, 'base/hub'),
            'pretrained_model_name_or_path': 'gpt2-xl'
        },
        'download_function': GPT2TokenizerFast.from_pretrained
    },
    {
        'download_params': {
            'cache_dir': os.path.join(prefix_dir, 'base/hub'),
            'pretrained_model_name_or_path': 'distilgpt2'
        },
        'download_function': GPT2TokenizerFast.from_pretrained
    },
    {
        'download_params': {
            'urls': ["https://huggingface.co/shibing624/text2vec-base-chinese/tree/main"],
            'file_save_paths': [os.path.join(prefix_dir, 'embedding',"shibing624_text2vec-base-chinese")]
        },
        'download_function': hg.get_batch_data
    }

]


def install():
    for model in model_config:
        print(json.dumps(model.get('download_params')))
        model.get('download_function')(**model.get('download_params'))


if __name__ == '__main__':
    install()
