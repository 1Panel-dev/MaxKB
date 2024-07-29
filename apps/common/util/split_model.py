# coding=utf-8
"""
    @project: qabot
    @Author：虎
    @file： split_model.py
    @date：2023/9/1 15:12
    @desc:
"""
import re
from functools import reduce
from typing import List, Dict

import jieba


def get_level_block(text, level_content_list, level_content_index, cursor):
    """
    从文本中获取块数据
    :param text: 文本
    :param level_content_list: 拆分的title数组
    :param level_content_index: 指定的下标
    :param cursor: 开始的下标位置
    :return: 拆分后的文本数据
    """
    start_content: str = level_content_list[level_content_index].get('content')
    next_content = level_content_list[level_content_index + 1].get("content") if level_content_index + 1 < len(
        level_content_list) else None
    start_index = text.index(start_content, cursor)
    end_index = text.index(next_content, start_index + 1) if next_content is not None else len(text)
    return text[start_index+len(start_content):end_index], end_index


def to_tree_obj(content, state='title'):
    """
    转换为树形对象
    :param content: 文本数据
    :param state:   状态: title block
    :return: 转换后的数据
    """
    return {'content': content, 'state': state}


def remove_special_symbol(str_source: str):
    """
    删除特殊字符
    :param str_source: 需要删除的文本数据
    :return: 删除后的数据
    """
    return str_source


def filter_special_symbol(content: dict):
    """
    过滤文本中的特殊字符
    :param content: 需要过滤的对象
    :return: 过滤后返回
    """
    content['content'] = remove_special_symbol(content['content'])
    return content


def flat(tree_data_list: List[dict], parent_chain: List[dict], result: List[dict]):
    """
    扁平化树形结构数据
    :param tree_data_list: 树形接口数据
    :param parent_chain:   父级数据 传[] 用于递归存储数据
    :param result:         响应数据 传[] 用于递归存放数据
    :return: result 扁平化后的数据
    """
    if parent_chain is None:
        parent_chain = []
    if result is None:
        result = []
    for tree_data in tree_data_list:
        p = parent_chain.copy()
        p.append(tree_data)
        result.append(to_flat_obj(parent_chain, content=tree_data["content"], state=tree_data["state"]))
        children = tree_data.get('children')
        if children is not None and len(children) > 0:
            flat(children, p, result)
    return result


def to_paragraph(obj: dict):
    """
    转换为段落
    :param obj: 需要转换的对象
    :return: 段落对象
    """
    content = obj['content']
    return {"keywords": get_keyword(content),
            'parent_chain': list(map(lambda p: p['content'], obj['parent_chain'])),
            'content': ",".join(list(map(lambda p: p['content'], obj['parent_chain']))) + content}


def get_keyword(content: str):
    """
    获取content中的关键词
    :param content: 文本
    :return: 关键词数组
    """
    stopwords = ['：', '“', '！', '”', '\n', '\\s']
    cutworms = jieba.lcut(content)
    return list(set(list(filter(lambda k: (k not in stopwords) | len(k) > 1, cutworms))))


def titles_to_paragraph(list_title: List[dict]):
    """
    将同一父级的title转换为块段落
    :param list_title: 同父级title
    :return: 块段落
    """
    if len(list_title) > 0:
        content = "\n,".join(
            list(map(lambda d: d['content'].strip("\r\n").strip("\n").strip("\\s"), list_title)))

        return {'keywords': '',
                'parent_chain': list(
                    map(lambda p: p['content'].strip("\r\n").strip("\n").strip("\\s"), list_title[0]['parent_chain'])),
                'content': ",".join(list(
                    map(lambda p: p['content'].strip("\r\n").strip("\n").strip("\\s"),
                        list_title[0]['parent_chain']))) + content}
    return None


def parse_group_key(level_list: List[dict]):
    """
    将同级别同父级的title生成段落,加上本身的段落数据形成新的数据
    :param level_list: title n 级数据
    :return: 根据title生成的数据 + 段落数据
    """
    result = []
    group_data = group_by(list(filter(lambda f: f['state'] == 'title' and len(f['parent_chain']) > 0, level_list)),
                          key=lambda d: ",".join(list(map(lambda p: p['content'], d['parent_chain']))))
    result += list(map(lambda group_data_key: titles_to_paragraph(group_data[group_data_key]), group_data))
    result += list(map(to_paragraph, list(filter(lambda f: f['state'] == 'block', level_list))))
    return result


def to_block_paragraph(tree_data_list: List[dict]):
    """
    转换为块段落对象
    :param tree_data_list: 树数据
    :return: 块段落
    """
    flat_list = flat(tree_data_list, [], [])
    level_group_dict: dict = group_by(flat_list, key=lambda f: f['level'])
    return list(map(lambda level: parse_group_key(level_group_dict[level]), level_group_dict))


def parse_title_level(text, content_level_pattern: List, index):
    if index >= len(content_level_pattern):
        return []
    result = parse_level(text, content_level_pattern[index])
    if len(result) == 0 and len(content_level_pattern) > index:
        return parse_title_level(text, content_level_pattern, index + 1)
    return result


def parse_level(text, pattern: str):
    """
    获取正则匹配到的文本
    :param text: 需要匹配的文本
    :param pattern:  正则
    :return: 符合正则的文本
    """
    level_content_list = list(map(to_tree_obj, [r[0:255] for r in re_findall(pattern, text) if r is not None]))
    return list(map(filter_special_symbol, level_content_list))


def re_findall(pattern, text):
    result = re.findall(pattern, text, flags=0)
    return list(filter(lambda r: r is not None and len(r) > 0, reduce(lambda x, y: [*x, *y], list(
        map(lambda row: [*(row if isinstance(row, tuple) else [row])], result)),
                                                                      [])))


def to_flat_obj(parent_chain: List[dict], content: str, state: str):
    """
    将树形属性转换为扁平对象
    :param parent_chain:
    :param content:
    :param state:
    :return:
    """
    return {'parent_chain': parent_chain, 'level': len(parent_chain), "content": content, 'state': state}


def flat_map(array: List[List]):
    """
    将二位数组转为一维数组
    :param array: 二维数组
    :return: 一维数组
    """
    result = []
    for e in array:
        result += e
    return result


def group_by(list_source: List, key):
    """
    將數組分組
    :param list_source: 需要分組的數組
    :param key: 分組函數
    :return: key->[]
    """
    result = {}
    for e in list_source:
        k = key(e)
        array = result.get(k) if k in result else []
        array.append(e)
        result[k] = array
    return result


def result_tree_to_paragraph(result_tree: List[dict], result, parent_chain, with_filter: bool):
    """
    转换为分段对象
    :param result_tree: 解析文本的树
    :param result:      传[]  用于递归
    :param parent_chain: 传[] 用户递归存储数据
    :param with_filter: 是否过滤block
    :return: List[{'problem':'xx','content':'xx'}]
    """
    for item in result_tree:
        if item.get('state') == 'block':
            result.append({'title': " ".join(parent_chain),
                           'content': filter_special_char(item.get("content")) if with_filter else item.get("content")})
        children = item.get("children")
        if children is not None and len(children) > 0:
            result_tree_to_paragraph(children, result,
                                     [*parent_chain, remove_special_symbol(item.get('content'))], with_filter)
    return result


def post_handler_paragraph(content: str, limit: int):
    """
    根据文本的最大字符分段
    :param content: 需要分段的文本字段
    :param limit:   最大分段字符
    :return: 分段后数据
    """
    result = []
    temp_char, start = '', 0
    while (pos := content.find("\n", start)) != -1:
        split, start = content[start:pos + 1], pos + 1
        if len(temp_char + split) > limit:
            result.append(temp_char)
            temp_char = ''
        temp_char = temp_char + split
    temp_char = temp_char + content[start:]
    if len(temp_char) > 0:
        result.append(temp_char)

    pattern = "[\\S\\s]{1," + str(limit) + '}'
    # 如果\n 单段超过限制,则继续拆分
    return reduce(lambda x, y: [*x, *y], map(lambda row: re.findall(pattern, row), result), [])


replace_map = {
    re.compile('\n+'): '\n',
    re.compile(' +'): ' ',
    re.compile('#+'): "",
    re.compile("\t+"): ''
}


def filter_special_char(content: str):
    """
    过滤特殊字段
    :param content: 文本
    :return: 过滤后字段
    """
    items = replace_map.items()
    for key, value in items:
        content = re.sub(key, value, content)
    return content


class SplitModel:

    def __init__(self, content_level_pattern, with_filter=True, limit=100000):
        self.content_level_pattern = content_level_pattern
        self.with_filter = with_filter
        if limit is None or limit > 100000:
            limit = 100000
        if limit < 50:
            limit = 50
        self.limit = limit

    def parse_to_tree(self, text: str, index=0):
        """
         解析文本
        :param text: 需要解析的文本
        :param index: 从那个正则开始解析
        :return: 解析后的树形结果数据
        """
        level_content_list = parse_title_level(text, self.content_level_pattern, index)
        if len(level_content_list) == 0:
            return list(map(lambda row: to_tree_obj(row, 'block'), post_handler_paragraph(text, limit=self.limit)))
        if index == 0 and text.lstrip().index(level_content_list[0]["content"].lstrip()) != 0:
            level_content_list.insert(0, to_tree_obj(""))

        cursor = 0
        for i in range(len(level_content_list)):
            block, cursor = get_level_block(text, level_content_list, i, cursor)
            if len(block) == 0:
                level_content_list[i]['children'] = [to_tree_obj("", "block")]
                continue
            children = self.parse_to_tree(text=block, index=index + 1)
            level_content_list[i]['children'] = children
            first_child_idx_in_block = block.lstrip().index(children[0]["content"].lstrip())
            if first_child_idx_in_block != 0:
                inner_children = self.parse_to_tree(block[:first_child_idx_in_block], index + 1)
                level_content_list[i]['children'].extend(inner_children)
        return level_content_list

    def parse(self, text: str):
        """
        解析文本
        :param text: 文本数据
        :return: 解析后数据 {content:段落数据,keywords:[‘段落关键词’],parent_chain:['段落父级链路']}
        """
        text = text.replace('\r\n', '\n')
        text = text.replace('\r', '\n')
        text = text.replace("\0", '')
        result_tree = self.parse_to_tree(text, 0)
        result = result_tree_to_paragraph(result_tree, [], [], self.with_filter)
        return [item for item in [self.post_reset_paragraph(row) for row in result] if
                'content' in item and len(item.get('content').strip()) > 0]

    def post_reset_paragraph(self, paragraph: Dict):
        result = self.filter_title_special_characters(paragraph)
        result = self.sub_title(result)
        result = self.content_is_null(result)
        return result

    @staticmethod
    def sub_title(paragraph: Dict):
        if 'title' in paragraph:
            title = paragraph.get('title')
            if len(title) > 255:
                return {**paragraph, 'title': title[0:255], 'content': title[255:len(title)] + paragraph.get('content')}
        return paragraph

    @staticmethod
    def content_is_null(paragraph: Dict):
        if 'title' in paragraph:
            title = paragraph.get('title')
            content = paragraph.get('content')
            if (content is None or len(content.strip()) == 0) and (title is not None and len(title) > 0):
                return {'title': '', 'content': title}
        return paragraph

    @staticmethod
    def filter_title_special_characters(paragraph: Dict):
        title = paragraph.get('title') if 'title' in paragraph else ''
        for title_special_characters in title_special_characters_list:
            title = title.replace(title_special_characters, '')
        return {**paragraph,
                'title': title}


title_special_characters_list = ['#', '\n', '\r', '\\s']

default_split_pattern = {
    'md': [re.compile('(?<=^)# .*|(?<=\\n)# .*'),
           re.compile('(?<=\\n)(?<!#)## (?!#).*|(?<=^)(?<!#)## (?!#).*'),
           re.compile("(?<=\\n)(?<!#)### (?!#).*|(?<=^)(?<!#)### (?!#).*"),
           re.compile("(?<=\\n)(?<!#)#### (?!#).*|(?<=^)(?<!#)#### (?!#).*"),
           re.compile("(?<=\\n)(?<!#)##### (?!#).*|(?<=^)(?<!#)##### (?!#).*"),
           re.compile("(?<=\\n)(?<!#)###### (?!#).*|(?<=^)(?<!#)###### (?!#).*")],
    'default': [re.compile("(?<!\n)\n\n+")]
}


def get_split_model(filename: str, with_filter: bool = False, limit: int = 100000):
    """
    根据文件名称获取分段模型
    :param limit:        每段大小
    :param with_filter: 是否过滤特殊字符
    :param filename: 文件名称
    :return: 分段模型
    """
    if filename.endswith(".md"):
        pattern_list = default_split_pattern.get('md')
        return SplitModel(pattern_list, with_filter=with_filter, limit=limit)

    pattern_list = default_split_pattern.get('md')
    return SplitModel(pattern_list, with_filter=with_filter, limit=limit)


def to_title_tree_string(result_tree: List):
    f = flat(result_tree, [], [])
    return "\n│".join(list(map(lambda r: title_tostring(r), list(filter(lambda row: row.get('state') == 'title', f)))))


def title_tostring(title_obj):
    f = "│ ".join(list(map(lambda index: " ", range(0, len(title_obj.get("parent_chain"))))))
    return f + "├───" + title_obj.get('content')
