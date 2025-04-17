from django.db import models
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from users.models import User


class ToolModule(MPTTModel):
    id = models.CharField(primary_key=True, max_length=64, editable=False, verbose_name="主键id")
    name = models.CharField(max_length=64, verbose_name="文件夹名称")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户id")
    workspace_id = models.CharField(max_length=64, verbose_name="工作空间id", default="default", db_index=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True)
    update_time = models.DateTimeField(verbose_name="修改时间", auto_now=True, null=True)

    class Meta:
        db_table = "tool_module"

    class MPTTMeta:
        order_insertion_by = ['name']
