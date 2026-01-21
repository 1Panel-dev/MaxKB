# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： ts_vecto_util.py
    @date：2024/4/16 15:26
    @desc:
"""
import re
import uuid_utils.compat as uuid
from typing import List

import jieba
import jieba.posseg

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
    j_word = str(uuid.uuid7())
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
    # 分词
    result = jieba.lcut(text, cut_all=True)
    # 转换为小写，确保英文词能被正确索引
    result_lower = [token.lower() for token in result]
    return " ".join(result_lower)


def to_query(text: str):
    # 中文停用词列表
    stopwords = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
                 '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
                 '自己', '这', '？', '！', '，', '。', '、', '；', '：', '"', '"', ''', ''',
                 '吗', '呢', '啊', '哦', '嗯', '吧', '呀', '什么', '怎么', '为什么', '哪里',
                 '谁', '哪个', '多少', '几', '怎样', '如何'}

    extract_tags = jieba.lcut(text, cut_all=True)

    # 过滤停用词和单字符（保留英文、数字）
    filtered_tags = []
    for tag in extract_tags:
        tag_stripped = tag.strip()
        # 保留：长度>1的词，或者是英文/数字
        if tag_stripped and (len(tag_stripped) > 1 or tag_stripped.isalnum()):
            if tag_stripped not in stopwords:
                # 转换为小写，确保与search_vector匹配
                filtered_tags.append(tag_stripped.lower())

    # 如果过滤后为空，使用原始分词（避免查询为空）
    if not filtered_tags:
        filtered_tags = [tag.strip().lower() for tag in extract_tags if tag.strip()]

    result = " ".join(filtered_tags)
    return result
