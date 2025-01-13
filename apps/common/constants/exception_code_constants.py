# coding=utf-8
"""
    @project: qabot
    @Author：虎
    @file： exception_code_constants.py
    @date：2023/9/4 14:09
    @desc: 异常常量类
"""
from enum import Enum

from common.exception.app_exception import AppApiException
from django.utils.translation import gettext_lazy as _


class ExceptionCodeConstantsValue:
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def get_message(self):
        return self.message

    def get_code(self):
        return self.code

    def to_app_api_exception(self):
        return AppApiException(code=self.code, message=self.message)


class ExceptionCodeConstants(Enum):
    INCORRECT_USERNAME_AND_PASSWORD = ExceptionCodeConstantsValue(1000, _('The username or password is incorrect'))
    NOT_AUTHENTICATION = ExceptionCodeConstantsValue(1001, _('Please log in first and bring the user Token'))
    EMAIL_SEND_ERROR = ExceptionCodeConstantsValue(1002, _('Email sending failed'))
    EMAIL_FORMAT_ERROR = ExceptionCodeConstantsValue(1003, _('Email format error'))
    EMAIL_IS_EXIST = ExceptionCodeConstantsValue(1004, _('The email has been registered, please log in directly'))
    EMAIL_IS_NOT_EXIST = ExceptionCodeConstantsValue(1005, _('The email is not registered, please register first'))
    CODE_ERROR = ExceptionCodeConstantsValue(1005,
                                             _('The verification code is incorrect or the verification code has expired'))
    USERNAME_IS_EXIST = ExceptionCodeConstantsValue(1006, _('The username has been registered, please log in directly'))
    USERNAME_ERROR = ExceptionCodeConstantsValue(1006,
                                                 _('The username cannot be empty and must be between 6 and 20 characters long.'))
    PASSWORD_NOT_EQ_RE_PASSWORD = ExceptionCodeConstantsValue(1007,
                                                              _('Password and confirmation password are inconsistent'))
