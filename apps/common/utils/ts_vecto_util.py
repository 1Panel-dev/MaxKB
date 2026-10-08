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
from jieba import analyse

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


# 疑问词、语气词等，对检索没有区分度
query_stop_words = {'请问', '怎么', '怎样', '如何', '什么', '为什么', '哪些', '哪个', '是否', '能否', '可以', '一下',
                    '我们', '你们', '他们', '这个', '那个', '哪里', '怎么办', '多少', '应该', '比较',
                    '另外', '还有', '以及', '了解', '吗', '呢', '吧', '啊', '的', '了', '是', '在', '和', '与',
                    '及', '或', '么', '着', '过', '也', '都', '就', '还', '又', '很', '我', '你', '他', '它', '有'}
# 低于该 idf 的词视为通用词
query_min_idf = 4.0
# 低于该 idf 的单字视为常用字，不参与未登录词合并
query_single_min_idf = 4.5
# 关键词数量上限，超出时按 idf 保留
query_max_keywords = 20
# 命中术语数量上限
query_max_terms = 10
# 未登录词合并的单字数量上限
query_max_single_run = 8
# 版本号、型号、邮箱等由连接符组成的整体，如 v2.1.2、gpt-4o、python3.11
query_compound_pattern = re.compile(r'[A-Za-z0-9]+(?:[._\-@:/][A-Za-z0-9]+)+')


def _get_query_keywords(text: str, tokenizer):
    idf_freq, median_idf = analyse.default_tfidf.idf_freq, analyse.default_tfidf.median_idf
    keywords = {}
    # 索引中 v2.1.2 被切分为相邻的 v2 1 2，使用短语查询 "v2 1 2" 要求按顺序相邻命中
    for compound in query_compound_pattern.findall(text):
        keywords.setdefault('"' + ' '.join(re.findall(r'[A-Za-z0-9]+', compound)) + '"', median_idf)
    text = query_compound_pattern.sub(' ', text)
    # HMM=False: 保证切出的词都能在 cut_all 构建的索引中找到
    tokens = [t.strip() for t in tokenizer.lcut(text, HMM=False)]
    single_run = []

    def flush_single_run():
        if len(single_run) >= 2:
            run = single_run[:query_max_single_run]
            # 权重取单字 idf 的均值，避免常用字组合排在实词前面
            keywords.setdefault(' '.join(run), sum(idf_freq.get(c, median_idf) for c in run) / len(run))
        single_run.clear()

    for token in tokens:
        if (len(token) == 1 and '\u4e00' <= token <= '\u9fff' and token not in query_stop_words
                and idf_freq.get(token, median_idf) >= query_single_min_idf):
            single_run.append(token)
            continue
        flush_single_run()
        if (len(token) < 2 or token.lower() in analyse.default_tfidf.stop_words or token in query_stop_words
                or token in remove_chars):
            continue
        if not any(c.isalnum() for c in token):
            continue
        idf = idf_freq.get(token, median_idf)
        if idf < query_min_idf:
            continue
        keywords.setdefault(token, idf)
    flush_single_run()
    if len(keywords) > query_max_keywords:
        # 词典外的英文词 idf 均为中位数，会整体高于中文词，因此中英文按占比分配名额，组内按 idf 取舍
        # 只按 idf 不乘词频，避免重复出现的词挤掉其他词；结果保持原文顺序
        keep = set()
        groups = [[k for k in keywords if k.isascii()], [k for k in keywords if not k.isascii()]]
        for group in groups:
            quota = round(query_max_keywords * len(group) / len(keywords))
            keep.update(sorted(group, key=keywords.get, reverse=True)[:quota])
        return [k for k in keywords if k in keep]
    return list(keywords)


def to_query(text: str, user_words: List[str] = None):
    tokenizer = _build_tokenizer(user_words) if user_words else jieba
    lower_text = text.lower()
    terms = list(dict.fromkeys(
        w.strip() for w in (user_words or []) if w and w.strip() and w.strip().lower() in lower_text))
    terms = [t.replace('"', ' ').lstrip('-') for t in sorted(terms, key=len, reverse=True)[:query_max_terms]]
    keywords = [k for k in _get_query_keywords(text, tokenizer) if k not in terms]

    clauses = terms + keywords
    if not clauses:
        clauses = list(dict.fromkeys(
            t.strip() for t in tokenizer.lcut(text, HMM=False)
            if t.strip() and t.strip() not in remove_chars and t.strip().lower() != 'or'
            and any(c.isalnum() for c in t)))[:query_max_keywords]
    return ' or '.join(clauses)
