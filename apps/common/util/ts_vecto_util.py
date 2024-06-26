# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： ts_vecto_util.py
    @date：2024/4/16 15:26
    @desc:
"""
import re
import uuid
from typing import List

import jieba
import jieba.posseg
from jieba import analyse

from common.util.split_model import group_by

jieba_word_list_cache = [chr(item) for item in range(38, 84)]

for jieba_word in jieba_word_list_cache:
    jieba.add_word('#' + jieba_word + '#')
# r"(?i)\b(?:https?|ftp|tcp|file)://[^\s]+\b",
# 某些不分词数据
# r'"([^"]*)"'
word_pattern_list = [r"v\d+.\d+.\d+",
                     r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}"]

remove_chars = '\n , :\'<>！@#￥%……&*（）!@#$%^&*()： ；，/"./'

jieba_remove_flag_list = ['x', 'w']


def get_word_list(text: str):
    result = []
    for pattern in word_pattern_list:
        word_list = re.findall(pattern, text)
        for child_list in word_list:
            for word in child_list if isinstance(child_list, tuple) else [child_list]:
                # 不能有: 所以再使用: 进行分割
                if word.__contains__(':'):
                    item_list = word.split(":")
                    for w in item_list:
                        result.append(w)
                else:
                    result.append(word)
    return result


def replace_word(word_dict, text: str):
    for key in word_dict:
        pattern = '(?<!#)' + re.escape(word_dict[key]) + '(?!#)'
        text = re.sub(pattern, key, text)
    return text


def get_word_key(text: str, use_word_list):
    j_word = next((j for j in jieba_word_list_cache if j not in text and all(j not in used for used in use_word_list)),
                  None)
    if j_word:
        return j_word
    j_word = str(uuid.uuid1())
    jieba.add_word(j_word)
    return j_word


def to_word_dict(word_list: List, text: str):
    word_dict = {}
    for word in word_list:
        key = get_word_key(text, set(word_dict))
        word_dict['#' + key + '#'] = word
    return word_dict


def get_key_by_word_dict(key, word_dict):
    v = word_dict.get(key)
    if v is None:
        return key
    return v


def to_ts_vector(text: str):
    # 获取不分词的数据
    word_list = get_word_list(text)
    # 获取关键词关系
    word_dict = to_word_dict(word_list, text)
    # 替换字符串
    text = replace_word(word_dict, text)
    # 分词
    filter_word = jieba.analyse.extract_tags(text, topK=100)
    result = jieba.lcut(text, HMM=True, use_paddle=True)
    # 过滤标点符号
    result = [item for item in result if filter_word.__contains__(item) and len(item) < 10]
    result_ = [{'word': get_key_by_word_dict(result[index], word_dict), 'index': index} for index in
               range(len(result))]
    result_group = group_by(result_, lambda r: r['word'])
    return " ".join(
        [f"{key.lower()}:{','.join([str(item['index'] + 1) for item in result_group[key]][:20])}" for key in
         result_group if
         not remove_chars.__contains__(key) and len(key.strip()) >= 0])


def to_query(text: str):
    # 获取不分词的数据
    word_list = get_word_list(text)
    # 获取关键词关系
    word_dict = to_word_dict(word_list, text)
    # 替换字符串
    text = replace_word(word_dict, text)
    extract_tags = analyse.extract_tags(text, topK=5, withWeight=True, allowPOS=('ns', 'n', 'vn', 'v', 'eng'))
    result = " ".join([get_key_by_word_dict(word, word_dict) for word, score in extract_tags if
                       not remove_chars.__contains__(word)])
    # 删除词库
    for word in word_list:
        jieba.del_word(word)
    return result
