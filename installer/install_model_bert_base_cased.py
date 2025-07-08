# coding=utf-8
import json
import os.path
from transformers import BertTokenizer

prefix_dir = "./model"
model_config = [
    {
        'download_params': {
            'cache_dir': os.path.join(prefix_dir, 'base/hub'),
            'pretrained_model_name_or_path': 'bert-base-cased'
        },
        'download_function': BertTokenizer.from_pretrained
    },
]


def install():
    for model in model_config:
        print(json.dumps(model.get('download_params')))
        model.get('download_function')(**model.get('download_params'))


if __name__ == '__main__':
    install()
