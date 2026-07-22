# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎虎
    @file： form_content.py
    @date：2026/7/6 15:30
    @desc:
"""
from typing import List, Dict, Optional

from application.workflow.content_type import ContentType
from application.workflow.message.struct.content import Content, NodeInfo, Position
from application.workflow.status import Status


class FormContent(Content):
    def __init__(self, _id, form_field_list: List[Dict], form_content_format: str,
                 is_submit: bool, status: Status, node_info: NodeInfo, position: Position,
                 form_data: Optional[Dict] = None, **kwargs):
        self.form_field_list = form_field_list
        self.form_content_format = form_content_format
        self.is_submit = is_submit
        self.form_data = form_data or {}
        super().__init__(_id, status, ContentType.FORM, node_info, position, **kwargs)

    def to_dict(self):
        result = super().to_dict()
        result['form_field_list'] = self.form_field_list
        result['form_content_format'] = self.form_content_format
        result['is_submit'] = self.is_submit
        result['form_data'] = self.form_data
        return result
