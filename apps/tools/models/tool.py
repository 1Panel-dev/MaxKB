import uuid_utils.compat as uuid
from django.db import models
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from common.mixins.app_model_mixin import AppModelMixin
from users.models import User


class ToolFolder(MPTTModel, AppModelMixin):
    id = models.CharField(primary_key=True, max_length=64, editable=False, verbose_name="主键id")
    name = models.CharField(max_length=64, verbose_name="文件夹名称", db_index=True)
    desc = models.CharField(max_length=200, null=True, blank=True, verbose_name="描述")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, db_constraint=False, blank=True, null=True)
    workspace_id = models.CharField(max_length=64, verbose_name="工作空间id", default="default", db_index=True)
    parent = TreeForeignKey('self', on_delete=models.DO_NOTHING, null=True, blank=True, related_name='children')

    class Meta:
        db_table = "tool_folder"

    class MPTTMeta:
        order_insertion_by = ['name']


class ToolScope(models.TextChoices):
    SHARED = "SHARED", '共享'
    WORKSPACE = "WORKSPACE", "工作空间可用"
    INTERNAL = "INTERNAL", '内置'


class ToolType(models.TextChoices):
    INTERNAL = "INTERNAL", '内置'
    CUSTOM = "CUSTOM", "自定义"
    MCP = "MCP", "MCP工具"


class Tool(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, db_constraint=False, blank=True, null=True)
    name = models.CharField(max_length=64, verbose_name="工具名称", db_index=True)
    desc = models.CharField(max_length=128, verbose_name="描述")
    code = models.CharField(max_length=102400, verbose_name="python代码")
    input_field_list = models.JSONField(verbose_name="输入字段列表", default=list)
    init_field_list = models.JSONField(verbose_name="启动字段列表", default=list)
    icon = models.CharField(max_length=256, verbose_name="工具库icon", default="")
    is_active = models.BooleanField(default=True, db_index=True)
    scope = models.CharField(max_length=20, verbose_name='可用范围', choices=ToolScope.choices,
                             default=ToolScope.WORKSPACE, db_index=True)
    tool_type = models.CharField(max_length=20, verbose_name='工具类型', choices=ToolType.choices,
                                 default=ToolType.CUSTOM, db_index=True)
    template_id = models.CharField(max_length=128, verbose_name="模版id", null=True, default=None, db_index=True)
    folder = models.ForeignKey(ToolFolder, on_delete=models.DO_NOTHING, verbose_name="文件夹id", default='default')
    workspace_id = models.CharField(max_length=64, verbose_name="工作空间id", default="default", db_index=True)
    init_params = models.CharField(max_length=102400, verbose_name="初始化参数", null=True)
    label = models.CharField(max_length=128, verbose_name="标签", null=True, db_index=True)
    version = models.CharField(max_length=64, verbose_name="版本号", null=True, default=None)

    class Meta:
        db_table = "tool"
