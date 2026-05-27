# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： ts_vecto_util.py
    @date：2024/4/16 15:26
    @desc:
"""
import re
import time
from threading import RLock
from typing import Dict, List, Tuple

import jieba
import jieba.posseg
import uuid_utils.compat as uuid

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

tokenizer_cache_ttl = 60 * 60
tokenizer_cache: Dict[Tuple[str, ...], Tuple[float, jieba.Tokenizer]] = {}
tokenizer_cache_lock = RLock()


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


def _build_tokenizer(user_words: List[str] = None):
    """创建分词器实例，相同用户词配置缓存 1 小时"""
    cache_key = tuple(word for word in (user_words or []) if word)
    now = time.time()
    with tokenizer_cache_lock:
        cache_value = tokenizer_cache.get(cache_key)
        if cache_value is not None and now - cache_value[0] < tokenizer_cache_ttl:
            return cache_value[1]
        for key, value in list(tokenizer_cache.items()):
            if now - value[0] >= tokenizer_cache_ttl:
                tokenizer_cache.pop(key, None)

    tokenizer = jieba.Tokenizer()
    if user_words:
        for word in user_words:
            if word:
                tokenizer.add_word(word)
    with tokenizer_cache_lock:
        tokenizer_cache[cache_key] = (time.time(), tokenizer)
    return tokenizer


def to_ts_vector(text: str, user_words: List[str] = None):
    # 分词
    tokenizer = _build_tokenizer(user_words) if user_words else jieba
    result = tokenizer.lcut(text, cut_all=True)
    return " ".join(result)


def to_query(text: str, user_words: List[str] = None):
    tokenizer = _build_tokenizer(user_words) if user_words else jieba
    extract_tags = tokenizer.lcut(text, cut_all=True)
    result = " ".join(extract_tags)
    return result
