# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： data_set.py
    @date：2023/9/21 9:35
    @desc: 数据集
"""
import uuid

from django.db import models
from django.db.models import QuerySet

from common.db.sql_execute import select_one
from common.mixins.app_model_mixin import AppModelMixin
from setting.models import Model
from users.models import User


class Status(models.TextChoices):
    """订单类型"""
    embedding = 0, '导入中'
    success = 1, '已完成'
    error = 2, '导入失败'
    queue_up = 3, '排队中'


class Type(models.TextChoices):
    base = 0, '通用类型'

    web = 1, 'web站点类型'


class HitHandlingMethod(models.TextChoices):
    optimization = 'optimization', '模型优化'
    directly_return = 'directly_return', '直接返回'


def default_model():
    return uuid.UUID('42f63a3d-427e-11ef-b3ec-a8a1595801ab')


class DataSet(AppModelMixin):
    """
    数据集表
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    name = models.CharField(max_length=150, verbose_name="数据集名称")
    desc = models.CharField(max_length=256, verbose_name="数据库描述")
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="所属用户")
    type = models.CharField(verbose_name='类型', max_length=1, choices=Type.choices,
                            default=Type.base)
    embedding_mode = models.ForeignKey(Model, on_delete=models.DO_NOTHING, verbose_name="向量模型",
                                       default=default_model)
    meta = models.JSONField(verbose_name="元数据", default=dict)

    class Meta:
        db_table = "dataset"


class Document(AppModelMixin):
    """
    文档表
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    dataset = models.ForeignKey(DataSet, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=150, verbose_name="文档名称")
    char_length = models.IntegerField(verbose_name="文档字符数 冗余字段")
    status = models.CharField(verbose_name='状态', max_length=1, choices=Status.choices,
                              default=Status.queue_up)
    is_active = models.BooleanField(default=True)

    type = models.CharField(verbose_name='类型', max_length=1, choices=Type.choices,
                            default=Type.base)
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
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    document = models.ForeignKey(Document, on_delete=models.DO_NOTHING, db_constraint=False)
    dataset = models.ForeignKey(DataSet, on_delete=models.DO_NOTHING)
    content = models.CharField(max_length=102400, verbose_name="段落内容")
    title = models.CharField(max_length=256, verbose_name="标题", default="")
    status = models.CharField(verbose_name='状态', max_length=1, choices=Status.choices,
                              default=Status.embedding)
    hit_num = models.IntegerField(verbose_name="命中次数", default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "paragraph"


class Problem(AppModelMixin):
    """
    问题表
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    dataset = models.ForeignKey(DataSet, on_delete=models.DO_NOTHING, db_constraint=False)
    content = models.CharField(max_length=256, verbose_name="问题内容")
    hit_num = models.IntegerField(verbose_name="命中次数", default=0)

    class Meta:
        db_table = "problem"


class ProblemParagraphMapping(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    dataset = models.ForeignKey(DataSet, on_delete=models.DO_NOTHING, db_constraint=False)
    document = models.ForeignKey(Document, on_delete=models.DO_NOTHING)
    problem = models.ForeignKey(Problem, on_delete=models.DO_NOTHING, db_constraint=False)
    paragraph = models.ForeignKey(Paragraph, on_delete=models.DO_NOTHING, db_constraint=False)

    class Meta:
        db_table = "problem_paragraph_mapping"


class Image(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    image = models.BinaryField(verbose_name="图片数据")
    image_name = models.CharField(max_length=256, verbose_name="图片名称", default="")

    class Meta:
        db_table = "image"


class File(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")

    file_name = models.CharField(max_length=256, verbose_name="文件名称", default="")

    loid = models.IntegerField(verbose_name="loid")

    class Meta:
        db_table = "file"

    def save(
            self, bytea=None, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        result = select_one("SELECT lo_from_bytea(%s, %s::bytea) as loid", [0, bytea])
        self.loid = result['loid']
        self.file_name = 'speech.mp3'
        super().save()

    def get_byte(self):
        result = select_one(f'SELECT lo_get({self.loid}) as "data"', [])
        return result['data']
