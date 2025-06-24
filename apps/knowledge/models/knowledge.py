from enum import Enum

import uuid_utils.compat as uuid
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.db.models import QuerySet
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from common.db.sql_execute import select_one
from common.mixins.app_model_mixin import AppModelMixin
from common.utils.common import get_sha256_hash
from models_provider.models import Model
from users.models import User


class KnowledgeType(models.IntegerChoices):
    BASE = 0, '通用类型'
    WEB = 1, 'web站点类型'
    LARK = 2, '飞书类型'
    YUQUE = 3, '语雀类型'


class TaskType(Enum):
    # 向量
    EMBEDDING = 1
    # 生成问题
    GENERATE_PROBLEM = 2
    # 同步
    SYNC = 3


class State(Enum):
    # 等待
    PENDING = '0'
    # 执行中
    STARTED = '1'
    # 成功
    SUCCESS = '2'
    # 失败
    FAILURE = '3'
    # 取消任务
    REVOKE = '4'
    # 取消成功
    REVOKED = '5'
    # 忽略
    IGNORED = 'n'


class KnowledgeScope(models.TextChoices):
    SHARED = "SHARED", '共享'
    WORKSPACE = "WORKSPACE", "工作空间可用"


class HitHandlingMethod(models.TextChoices):
    optimization = 'optimization', '模型优化'
    directly_return = 'directly_return', '直接返回'


class Status:
    type_cls = TaskType
    state_cls = State

    def __init__(self, status: str = None):
        self.task_status = {}
        status_list = list(status[::-1] if status is not None else '')
        for _type in self.type_cls:
            index = _type.value - 1
            _state = self.state_cls(status_list[index] if len(status_list) > index else 'n')
            self.task_status[_type] = _state

    @staticmethod
    def of(status: str):
        return Status(status)

    def __str__(self):
        result = []
        for _type in sorted(self.type_cls, key=lambda item: item.value, reverse=True):
            result.insert(len(self.type_cls) - _type.value, self.task_status[_type].value)
        return ''.join(result)

    def __setitem__(self, key, value):
        self.task_status[key] = value

    def __getitem__(self, item):
        return self.task_status[item]

    def update_status(self, task_type: TaskType, state: State):
        self.task_status[task_type] = state


def default_status_meta():
    return {"state_time": {}}




class KnowledgeFolder(MPTTModel, AppModelMixin):
    id = models.CharField(primary_key=True, max_length=64, editable=False, verbose_name="主键id")
    name = models.CharField(max_length=64, verbose_name="文件夹名称")
    desc = models.CharField(max_length=200, null=True, blank=True, verbose_name="描述")
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="用户id")
    workspace_id = models.CharField(max_length=64, verbose_name="工作空间id", default="default", db_index=True)
    parent = TreeForeignKey('self', on_delete=models.DO_NOTHING, null=True, blank=True, related_name='children')

    class Meta:
        db_table = "knowledge_folder"

    class MPTTMeta:
        order_insertion_by = ['name']


class Knowledge(AppModelMixin):
    """
    知识库表
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    name = models.CharField(max_length=150, verbose_name="知识库名称")
    workspace_id = models.CharField(max_length=64, verbose_name="工作空间id", default="default", db_index=True)
    desc = models.CharField(max_length=256, verbose_name="描述")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, db_constraint=False, blank=True, null=True)
    type = models.IntegerField(verbose_name='类型', choices=KnowledgeType.choices, default=KnowledgeType.BASE)
    scope = models.CharField(max_length=20, verbose_name='可用范围', choices=KnowledgeScope.choices,
                             default=KnowledgeScope.WORKSPACE)
    folder = models.ForeignKey(KnowledgeFolder, on_delete=models.DO_NOTHING, verbose_name="文件夹id", default='default')
    embedding_model = models.ForeignKey(Model, on_delete=models.DO_NOTHING, verbose_name="向量模型")
    file_size_limit = models.IntegerField(verbose_name="文件大小限制", default=100)
    file_count_limit = models.IntegerField(verbose_name="文件数量限制", default=50)
    meta = models.JSONField(verbose_name="元数据", default=dict)

    class Meta:
        db_table = "knowledge"


class Document(AppModelMixin):
    """
    文档表
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    knowledge = models.ForeignKey(Knowledge, on_delete=models.DO_NOTHING, verbose_name="知识库id")
    name = models.CharField(max_length=150, verbose_name="文档名称")
    char_length = models.IntegerField(verbose_name="文档字符数 冗余字段")
    status = models.CharField(verbose_name='状态', max_length=20, default=Status('').__str__)
    status_meta = models.JSONField(verbose_name="状态统计数据", default=default_status_meta)
    is_active = models.BooleanField(default=True)
    type = models.IntegerField(verbose_name='类型', choices=KnowledgeType.choices, default=KnowledgeType.BASE)
    hit_handling_method = models.CharField(verbose_name='命中处理方式', max_length=20,
                                           choices=HitHandlingMethod.choices,
                                           default=HitHandlingMethod.optimization)
    directly_return_similarity = models.FloatField(verbose_name='直接回答相似度', default=0.9)

    meta = models.JSONField(verbose_name="元数据", default=dict)

    class Meta:
        db_table = "document"


class Paragraph(AppModelMixin):
    """
    段落表
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    document = models.ForeignKey(Document, on_delete=models.DO_NOTHING, db_constraint=False)
    knowledge = models.ForeignKey(Knowledge, on_delete=models.DO_NOTHING)
    content = models.CharField(max_length=102400, verbose_name="段落内容")
    title = models.CharField(max_length=256, verbose_name="标题", default="")
    status = models.CharField(verbose_name='状态', max_length=20, default=Status('').__str__)
    status_meta = models.JSONField(verbose_name="状态数据", default=default_status_meta)
    hit_num = models.IntegerField(verbose_name="命中次数", default=0)
    is_active = models.BooleanField(default=True)
    position = models.IntegerField(verbose_name="段落顺序", default=0, db_index=True)

    class Meta:
        db_table = "paragraph"


class Problem(AppModelMixin):
    """
    问题表
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    knowledge = models.ForeignKey(Knowledge, on_delete=models.DO_NOTHING, db_constraint=False)
    content = models.CharField(max_length=256, verbose_name="问题内容")
    hit_num = models.IntegerField(verbose_name="命中次数", default=0)

    class Meta:
        db_table = "problem"


class ProblemParagraphMapping(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    knowledge = models.ForeignKey(Knowledge, on_delete=models.DO_NOTHING, db_constraint=False)
    document = models.ForeignKey(Document, on_delete=models.DO_NOTHING, db_constraint=False)
    problem = models.ForeignKey(Problem, on_delete=models.DO_NOTHING, db_constraint=False)
    paragraph = models.ForeignKey(Paragraph, on_delete=models.DO_NOTHING, db_constraint=False)

    class Meta:
        db_table = "problem_paragraph_mapping"


class SourceType(models.IntegerChoices):
    """订单类型"""
    PROBLEM = 0, '问题'
    PARAGRAPH = 1, '段落'
    TITLE = 2, '标题'


class SearchMode(models.TextChoices):
    embedding = 'embedding'
    keywords = 'keywords'
    blend = 'blend'


class FileSourceType(models.TextChoices):
    # 知识库  跟随知识库被删除而被删除 source_id 为知识库id
    KNOWLEDGE = "KNOWLEDGE"
    # 应用  跟随应用被删除而被删除 source_id 为应用id
    APPLICATION = "APPLICATION"
    # 工具  跟随工具被删除而被删除 source_id 为应用id
    TOOL = "TOOL"
    # 文档
    DOCUMENT = "DOCUMENT"
    # 临时30分钟 数据30分钟后被清理 source_id 为TEMPORARY_30_MINUTE
    TEMPORARY_30_MINUTE = "TEMPORARY_30_MINUTE"
    # 临时120分钟 数据120分钟后被清理 source_id为TEMPORARY_100_MINUTE
    TEMPORARY_120_MINUTE = "TEMPORARY_100_MINUTE"
    # 临时1天 数据1天后被清理 source_id为TEMPORARY_1_DAY
    TEMPORARY_1_DAY = "TEMPORARY_1_DAY"


class VectorField(models.Field):
    def db_type(self, connection):
        return 'vector'


class Embedding(models.Model):
    id = models.CharField(max_length=128, primary_key=True, verbose_name="主键id")
    source_id = models.CharField(max_length=128, verbose_name="资源id")
    source_type = models.CharField(verbose_name='资源类型', max_length=5, choices=SourceType.choices,
                                   default=SourceType.PROBLEM)
    is_active = models.BooleanField(verbose_name="是否可用", max_length=1, default=True)
    knowledge = models.ForeignKey(Knowledge, on_delete=models.DO_NOTHING, verbose_name="文档关联", db_constraint=False)
    document = models.ForeignKey(Document, on_delete=models.DO_NOTHING, verbose_name="文档关联", db_constraint=False)
    paragraph = models.ForeignKey(Paragraph, on_delete=models.DO_NOTHING, verbose_name="段落关联", db_constraint=False)
    embedding = VectorField(verbose_name="向量")
    search_vector = SearchVectorField(verbose_name="分词", default="")
    meta = models.JSONField(verbose_name="元数据", default=dict)

    class Meta:
        db_table = "embedding"


class File(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    file_name = models.CharField(max_length=256, verbose_name="文件名称", default="")
    file_size = models.IntegerField(verbose_name="文件大小", default=0)
    sha256_hash = models.CharField(verbose_name="文件sha256_hash标识", default="")
    source_type = models.CharField(verbose_name="资源类型", choices=FileSourceType,
                                   default=FileSourceType.TEMPORARY_120_MINUTE.value)
    source_id = models.CharField(verbose_name="资源id", default=FileSourceType.TEMPORARY_120_MINUTE.value)
    loid = models.IntegerField(verbose_name="loid")
    meta = models.JSONField(verbose_name="文件关联数据", default=dict)

    class Meta:
        db_table = "file"

    def save(self, bytea=None, force_insert=False, force_update=False, using=None, update_fields=None):
        sha256_hash = get_sha256_hash(bytea)
        f = QuerySet(File).filter(sha256_hash=sha256_hash).first()
        if f is not None:
            self.loid = f.loid
        else:
            result = select_one("SELECT lo_from_bytea(%s, %s::bytea) as loid", [0, bytea])
            self.loid = result['loid']
        self.file_size = len(bytea)
        self.sha256_hash = sha256_hash
        super().save()

    def get_bytes(self):
        result = select_one(f'SELECT lo_get({self.loid}) as "data"', [])
        return result['data']


@receiver(pre_delete, sender=File)
def on_delete_file(sender, instance, **kwargs):
    exist = QuerySet(File).filter(loid=instance.loid).exclude(id=instance.id).exists()
    if not exist:
        select_one(f'SELECT lo_unlink({instance.loid})', [])
