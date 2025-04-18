import uuid_utils.compat as uuid
from django.db import models

from users.models import User
from .tool_module import ToolModule


class ToolScope(models.TextChoices):
    SHARED = "SHARED", '共享'
    WORKSPACE = "WORKSPACE", "工作空间可用"


class Tool(models.Model):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户id")
    name = models.CharField(max_length=64, verbose_name="函数名称")
    desc = models.CharField(max_length=128, verbose_name="描述")
    code = models.CharField(max_length=102400, verbose_name="python代码")
    input_field_list = models.JSONField(verbose_name="输入字段列表", default=list)
    init_field_list = models.JSONField(verbose_name="启动字段列表", default=list)
    icon = models.CharField(max_length=256, verbose_name="函数库icon", default="/ui/favicon.ico")
    is_active = models.BooleanField(default=True)
    scope = models.CharField(max_length=20, verbose_name='可用范围', choices=ToolScope.choices,
                             default=ToolScope.WORKSPACE)
    template_id = models.UUIDField(max_length=128, verbose_name="模版id", null=True, default=None)
    module = models.ForeignKey(ToolModule, on_delete=models.CASCADE, verbose_name="模块id", default='root')
    workspace_id = models.CharField(max_length=64, verbose_name="工作空间id", default="default", db_index=True)
    init_params = models.CharField(max_length=102400, verbose_name="初始化参数", null=True)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True)
    update_time = models.DateTimeField(verbose_name="修改时间", auto_now=True, null=True)

    class Meta:
        db_table = "tool"
