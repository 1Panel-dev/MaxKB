# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： base_parse_qa_handle.py
    @date：2024/5/21 14:56
    @desc:
"""
from abc import ABC, abstractmethod


def get_row_value(row, title_row_index_dict, field):
    index = title_row_index_dict.get(field)
    if index is None:
        return None
    if (len(row) - 1) >= index:
        return row[index]
    return None


def get_title_row_index_dict(title_row_list):
    title_row_index_dict = {}
    if len(title_row_list) == 1:
        title_row_index_dict['content'] = 0
    elif len(title_row_list) == 1:
        title_row_index_dict['title'] = 0
        title_row_index_dict['content'] = 1
    else:
        title_row_index_dict['title'] = 0
        title_row_index_dict['content'] = 1
        title_row_index_dict['problem_list'] = 2
    for index in range(len(title_row_list)):
        title_row = title_row_list[index]
        if title_row is None:
            title_row = ''
        if title_row.startswith('分段标题'):
            title_row_index_dict['title'] = index
        if title_row.startswith('分段内容'):
            title_row_index_dict['content'] = index
        if title_row.startswith('问题'):
            title_row_index_dict['problem_list'] = index
    return title_row_index_dict


class BaseParseQAHandle(ABC):
    @abstractmethod
    def support(self, file, get_buffer):
        pass

    @abstractmethod
    def handle(self, file, get_buffer):
        pass
