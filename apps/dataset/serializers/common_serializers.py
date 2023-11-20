# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： common_serializers.py
    @date：2023/11/17 11:00
    @desc:
"""
import os

from common.db.sql_execute import update_execute
from common.util.file_util import get_file_content
from smartdoc.conf import PROJECT_DIR


def update_document_char_length(document_id: str):
    update_execute(get_file_content(
        os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'update_document_char_length.sql')),
        (document_id, document_id))
