# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： common.py
    @date：2024/12/11 17:57
    @desc:
"""


class Answer:
    def __init__(self, content, view_type, runtime_node_id, chat_record_id, child_node):
        self.view_type = view_type
        self.content = content
        self.runtime_node_id = runtime_node_id
        self.chat_record_id = chat_record_id
        self.child_node = child_node

    def to_dict(self):
        return {'view_type': self.view_type, 'content': self.content, 'runtime_node_id': self.runtime_node_id,
                'chat_record_id': self.chat_record_id, 'child_node': self.child_node}
