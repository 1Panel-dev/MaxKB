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
    INCORRECT_USERNAME_AND_PASSWORD = ExceptionCodeConstantsValue(1000, "用户名或者密码不正确")
    NOT_AUTHENTICATION = ExceptionCodeConstantsValue(1001, "请先登录,并携带用户Token")
    EMAIL_SEND_ERROR = ExceptionCodeConstantsValue(1002, "邮件发送失败")
    EMAIL_FORMAT_ERROR = ExceptionCodeConstantsValue(1003, "邮箱格式错误")
    EMAIL_IS_EXIST = ExceptionCodeConstantsValue(1004, "邮箱已经被注册,请勿重复注册")
    EMAIL_IS_NOT_EXIST = ExceptionCodeConstantsValue(1005, "邮箱尚未注册,请先注册")
    CODE_ERROR = ExceptionCodeConstantsValue(1005, "验证码不正确,或者验证码过期")
    USERNAME_IS_EXIST = ExceptionCodeConstantsValue(1006, "用户名已被使用,请使用其他用户名")
    USERNAME_ERROR = ExceptionCodeConstantsValue(1006, "用户名不能为空,并且长度在6-20")
    PASSWORD_NOT_EQ_RE_PASSWORD = ExceptionCodeConstantsValue(1007, "密码与确认密码不一致")
