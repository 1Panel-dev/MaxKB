# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： py_lint_serializer.py
    @date：2024/9/30 15:38
    @desc:
"""
import os
import uuid

from pylint.lint import Run
from pylint.reporters import JSON2Reporter
from rest_framework import serializers

from common.util.field_message import ErrMessage
from smartdoc.const import PROJECT_DIR
from django.utils.translation import gettext_lazy as _


class PyLintInstance(serializers.Serializer):
    code = serializers.CharField(required=True, allow_null=True, allow_blank=True,
                                 error_messages=ErrMessage.char(_('function content')))


def to_dict(message, file_name):
    return {'line': message.line,
            'column': message.column,
            'endLine': message.end_line,
            'endColumn': message.end_column,
            'message': (message.msg or "").replace(file_name, 'code'),
            'type': message.category}


def get_file_name():
    file_name = f"{uuid.uuid1()}"
    py_lint_dir = os.path.join(PROJECT_DIR, 'data', 'py_lint')
    if not os.path.exists(py_lint_dir):
        os.makedirs(py_lint_dir)
    return os.path.join(py_lint_dir, file_name)


class PyLintSerializer(serializers.Serializer):

    def pylint(self, instance, is_valid=True):
        if is_valid:
            self.is_valid(raise_exception=True)
            PyLintInstance(data=instance).is_valid(raise_exception=True)
        code = instance.get('code')
        file_name = get_file_name()
        with open(file_name, 'w') as file:
            file.write(code)
        reporter = JSON2Reporter()
        Run([file_name,
             "--disable=line-too-long",
             '--module-rgx=[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'],
            reporter=reporter, exit=False)
        os.remove(file_name)
        return [to_dict(m, os.path.basename(file_name)) for m in reporter.messages]
