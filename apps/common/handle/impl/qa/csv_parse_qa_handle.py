# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： csv_parse_qa_handle.py
    @date：2024/5/21 14:59
    @desc:
"""
import csv
import io

from charset_normalizer import detect

from common.handle.base_parse_qa_handle import BaseParseQAHandle


def read_csv_standard(file_path):
    data = []
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            data.append(row)
    return data


class CsvParseQAHandle(BaseParseQAHandle):
    def support(self, file, get_buffer):
        file_name: str = file.name.lower()
        if file_name.endswith(".csv"):
            return True
        return False

    def handle(self, file, get_buffer):
        buffer = get_buffer(file)
        reader = csv.reader(io.TextIOWrapper(io.BytesIO(buffer), encoding=detect(buffer)['encoding']))
        try:
            title_row_list = reader.__next__()
        except Exception as e:
            return []
        title_row_index_dict = {'title': 0, 'content': 1, 'problem_list': 2}
        for index in range(len(title_row_list)):
            title_row = title_row_list[index]
            if title_row.startswith('分段标题'):
                title_row_index_dict['title'] = index
            if title_row.startswith('分段内容'):
                title_row_index_dict['content'] = index
            if title_row.startswith('问题'):
                title_row_index_dict['problem_list'] = index
        paragraph_list = []
        for row in reader:
            problem = row[title_row_index_dict.get('problem_list')]
            problem_list = [{'content': p[0:255]} for p in problem.split('\n') if len(p.strip()) > 0]
            paragraph_list.append({'title': row[title_row_index_dict.get('title')][0:255],
                                   'content': row[title_row_index_dict.get('content')][0:4096],
                                   'problem_list': problem_list})
        return [{'name': file.name, 'paragraphs': paragraph_list}]
