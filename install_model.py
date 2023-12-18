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

from transformers import GPT2TokenizerFast
import sentence_transformers

prefix_dir = os.path.join(os.path.dirname(os.path.abspath(os.getcwd())), 'model')

model_config = [
    {
        'download_params': {
            'cache_dir': os.path.join(prefix_dir, 'base'),
            'pretrained_model_name_or_path': 'gpt2'
        },
        'download_function': GPT2TokenizerFast.from_pretrained
    },
    {
        'download_params': {
            'cache_dir': os.path.join(prefix_dir, 'base'),
            'pretrained_model_name_or_path': 'gpt2-medium'
        },
        'download_function': GPT2TokenizerFast.from_pretrained
    },
    {
        'download_params': {
            'cache_dir': os.path.join(prefix_dir, 'base'),
            'pretrained_model_name_or_path': 'gpt2-large'
        },
        'download_function': GPT2TokenizerFast.from_pretrained
    },
    {
        'download_params': {
            'cache_dir': os.path.join(prefix_dir, 'base'),
            'pretrained_model_name_or_path': 'gpt2-xl'
        },
        'download_function': GPT2TokenizerFast.from_pretrained
    },
    {
        'download_params': {
            'cache_dir': os.path.join(prefix_dir, 'base'),
            'pretrained_model_name_or_path': 'distilgpt2'
        },
        'download_function': GPT2TokenizerFast.from_pretrained
    },
    {
        'download_params': {
            'model_name_or_path': 'shibing624/text2vec-base-chinese',
            'cache_folder': os.path.join(prefix_dir, 'embedding')
        },
        'download_function': sentence_transformers.SentenceTransformer
    }

]


def install():
    for model in model_config:
        print(json.dumps(model.get('download_params')))
        model.get('download_function')(**model.get('download_params'))


if __name__ == '__main__':
    install()
