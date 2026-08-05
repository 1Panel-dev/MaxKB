# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎虎
    @file： operate_constants.py
    @date：2026/8/3 17:32
    @desc: 操作权限常量
"""
from enum import Enum
from django.utils.translation import gettext_lazy as _


class Operate(Enum):
    """
     一个权限组的操作权限
    """
    SELF = ("", "")
    READ = ("READ", _("Read"))
    EDIT = ("READ+EDIT", _("Edit"))
    CREATE = ("READ+CREATE", _("Create"))
    DELETE = ("READ+DELETE", _("Delete"))
    """
    使用权限
    """
    USE = ("USE", _("Use"))
    IMPORT = ("READ+IMPORT", _("Import"))
    EXPORT = ("READ+EXPORT", _("Export"))
    PUBLISH = ("READ+PUBLISH", _("Publish"))
    SYNC = ("READ+SYNC", _("Sync"))
    GENERATE = ("READ+GENERATE", _("Generate"))
    ADD_MEMBER = ("READ+ADD_MEMBER", _("Add Member"))
    REMOVE_MEMBER = ("READ+REMOVE_MEMBER", _("Remove Member"))
    VECTOR = ("READ+VECTOR", _("Vector"))
    MIGRATE = ("READ+MIGRATE", _("Migrate"))
    RELATE = ("READ+RELATE", _("Relate"))
    USER_GROUP = ("READ+USER_GROUP", _("User Group"))
    ANNOTATION = ("READ+ANNOTATION", _("Annotation"))
    CLEAR_POLICY = ("READ+CLEAR_POLICY", _("Clear Policy"))
    EMBED = ("READ+EMBED", _("Embed third party"))
    ACCESS = ("READ+ACCESS", _("Access restrictions"))
    DISPLAY = ("READ+DISPLAY", _("Display Settings"))
    API_KEY = ("READ+API_KEY", _("API KEY"))
    PUBLIC_ACCESS = ("READ+PUBLIC_ACCESS", _("Public access link"))
    Q_WEIXIN = ("READ+Q_WEIXIN", _("Enterprise WeiXin"))
    FEISHU = ("READ+FEISHU", _("Feishu"))
    DD = ("READ+DD", _("Dingding"))
    WEIXIN_PUBLIC_ACCOUNT = ("READ+WEIXIN_PUBLIC_ACCOUNT", _("Weixin Public Account"))
    SLACK = ("READ+SLACK", _("Slack"))
    ADD_KNOWLEDGE = ("READ+ADD_KNOWLEDGE", _("Add to Knowledge Base"))
    TO_CHAT = ("READ+TO_CHAT", _("To Chat"))
    SETTING = ("READ+SETTING", _("Setting"))
    DOWNLOAD = ("READ+DOWNLOAD", _("Download Original Document"))
    COPY = ("READ+COPY", _("Copy"))
    AUTH = ("READ+AUTH", _("resource authorization"))
    TAG = ("READ+TAG", _("Tag Setting"))
    REPLACE = ("READ+REPLACE", _("Replace Original Document"))
    UPDATE = ("READ+UPDATE", _("Update License"))
    RELATE_VIEW = ("READ+RELATE_VIEW", _("View related resources"))
    RECORD = ("READ+RECORD", _("Read execute record"))
    TRIGGER_READ = ("READ+TRIGGER_READ", _("Read Trigger"))
    TRIGGER_EDIT = ("READ+TRIGGER_EDIT", _("Edit Trigger"))
    TRIGGER_CREATE = ("READ+TRIGGER_CREATE", _("Create Trigger"))
    TRIGGER_DELETE = ("READ+TRIGGER_DELETE", _("Delete Trigger"))
    BATCH_DELETE = ("READ+BATCH_DELETE", _("Batch delete"))
    BATCH_MOVE = ("READ+BATCH_MOVE", _("Batch move"))
    TOKEN = ("READ+TOKEN", _("Token Index"))
    TO_WORKSPACE = ("READ+TO_WORKSPACE", _("Authorize to Workspace"))
    SET_ROLE = ("READ+SET_ROLE", _("Set Role"))

    def __init__(self, value, label):
        self._value_ = value
        self.label = label
