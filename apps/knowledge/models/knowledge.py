import uuid_utils.compat as uuid
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from common.db.sql_execute import select_one
from common.mixins.app_model_mixin import AppModelMixin
from models_provider.models import Model
from users.models import User


class KnowledgeType(models.IntegerChoices):
    BASE = 0, '通用类型'
    WEB = 1, 'web站点类型'
    LARK = 2, '飞书类型'
    YUQUE = 3, '语雀类型'


class KnowledgeScope(models.TextChoices):
    SHARED = "SHARED", '共享'
    WORKSPACE = "WORKSPACE", "工作空间可用"


def default_model():
    # todo : 这里需要从数据库中获取默认的模型
    return uuid.UUID('42f63a3d-427e-11ef-b3ec-a8a1595801ab')


class KnowledgeModule(MPTTModel, AppModelMixin):
    id = models.CharField(primary_key=True, max_length=64, editable=False, verbose_name="主键id")
    name = models.CharField(max_length=64, verbose_name="文件夹名称")
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="用户id")
    workspace_id = models.CharField(max_length=64, verbose_name="工作空间id", default="default", db_index=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class Meta:
        db_table = "knowledge_module"

    class MPTTMeta:
        order_insertion_by = ['name']



class Knowledge(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    name = models.CharField(max_length=150, verbose_name="知识库名称")
    workspace_id = models.CharField(max_length=64, verbose_name="工作空间id", default="default", db_index=True)
    desc = models.CharField(max_length=256, verbose_name="描述")
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="所属用户")
    type = models.IntegerField(verbose_name='类型', choices=KnowledgeType.choices, default=KnowledgeType.BASE)
    scope = models.CharField(max_length=20, verbose_name='可用范围', choices=KnowledgeScope.choices, default=KnowledgeScope.WORKSPACE)
    module = models.ForeignKey(KnowledgeModule, on_delete=models.CASCADE, verbose_name="模块id", default='root')
    embedding_model = models.ForeignKey(Model, on_delete=models.DO_NOTHING, verbose_name="向量模型",
                                       default=default_model)
    meta = models.JSONField(verbose_name="元数据", default=dict)

    class Meta:
        db_table = "knowledge"


class File(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    file_name = models.CharField(max_length=256, verbose_name="文件名称", default="")
    workspace_id = models.CharField(max_length=64, verbose_name="工作空间id", default="default", db_index=True)
    loid = models.IntegerField(verbose_name="loid")
    meta = models.JSONField(verbose_name="文件关联数据", default=dict)

    class Meta:
        db_table = "file"

    def save(self, bytea=None, force_insert=False, force_update=False, using=None, update_fields=None):
        result = select_one("SELECT lo_from_bytea(%s, %s::bytea) as loid", [0, bytea])
        self.loid = result['loid']
        super().save()

    def get_bytes(self):
        result = select_one(f'SELECT lo_get({self.loid}) as "data"', [])
        return result['data']


@receiver(pre_delete, sender=File)
def on_delete_file(sender, instance, **kwargs):
    select_one(f'SELECT lo_unlink({instance.loid})', [])
