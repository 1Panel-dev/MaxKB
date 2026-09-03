import io
import zipfile
from enum import Enum

import uuid_utils.compat as uuid
from common.db.sql_execute import select_one
from common.mixins.app_model_mixin import AppModelMixin
from common.storage.seaweedfs import get_bucket, get_s3_client, is_seaweedfs_enabled
from common.utils.common import get_sha256_hash
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.db.models import QuerySet
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from models_provider.models import Model
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from users.models import User


class KnowledgeType(models.IntegerChoices):
    BASE = 0, "通用类型"
    WEB = 1, "web站点类型"
    LARK = 2, "飞书类型"
    YUQUE = 3, "语雀类型"
    WORKFLOW = 4, "工作流类型"


class TaskType(Enum):
    # 向量
    EMBEDDING = 1
    # 生成问题
    GENERATE_PROBLEM = 2
    # 同步
    SYNC = 3
    # 分词索引
    TOKENIZE = 4


class State(Enum):
    # 等待
    PENDING = "0"
    # 执行中
    STARTED = "1"
    # 成功
    SUCCESS = "2"
    # 失败
    FAILURE = "3"
    # 取消任务
    REVOKE = "4"
    # 取消成功
    REVOKED = "5"
    # 忽略
    IGNORED = "n"


class KnowledgeScope(models.TextChoices):
    SHARED = "SHARED", "共享"
    WORKSPACE = "WORKSPACE", "工作空间可用"


class HitHandlingMethod(models.TextChoices):
    optimization = "optimization", "模型优化"
    directly_return = "directly_return", "直接返回"


class ContentOrigin(models.TextChoices):
    MANUAL = "manual", "手工创建"
    SYNCED = "synced", "外部同步"


class DocumentResourceType(models.TextChoices):
    DOCUMENT = "document", "文档"
    IMAGE = "image", "图片"


class LocalState(models.TextChoices):
    CLEAN = "clean", "未修改"
    MODIFIED = "modified", "本地已修改"
    DELETED = "deleted", "本地已删除"


class SyncState(models.TextChoices):
    ACTIVE = "active", "正常"
    REMOTE_DELETED = "remote_deleted", "远端已删除"
    CONFLICT = "conflict", "同步冲突"


class KnowledgeSyncType(models.TextChoices):
    INCREMENTAL = "incremental", "增量同步"
    REPLACE = "replace", "替换同步"
    COMPLETE = "complete", "完整同步"


class KnowledgeSyncStatus(models.TextChoices):
    RUNNING = "running", "同步中"
    SUCCESS = "success", "同步成功"
    FAILURE = "failure", "同步失败"


class KnowledgeSyncTrigger(models.TextChoices):
    MANUAL = "manual", "手动同步"
    SCHEDULED = "scheduled", "定时同步"


class AssetProcessStatus(models.TextChoices):
    PENDING = "pending", "待处理"
    SUCCESS = "success", "处理成功"
    FAILURE = "failure", "处理失败"
    SKIPPED = "skipped", "未启用"


class Status:
    type_cls = TaskType
    state_cls = State

    def __init__(self, status: str = None):
        self.task_status = {}
        status_list = list(status[::-1] if status is not None else "")
        for _type in self.type_cls:
            index = _type.value - 1
            _state = self.state_cls(status_list[index] if len(status_list) > index else "n")
            self.task_status[_type] = _state

    @staticmethod
    def of(status: str):
        return Status(status)

    def __str__(self):
        result = []
        for _type in sorted(self.type_cls, key=lambda item: item.value, reverse=True):
            result.insert(len(self.type_cls) - _type.value, self.task_status[_type].value)
        return "".join(result)

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
    name = models.CharField(max_length=64, verbose_name="文件夹名称", db_index=True)
    desc = models.CharField(max_length=200, null=True, blank=True, verbose_name="描述")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, db_constraint=False, blank=True, null=True)
    workspace_id = models.CharField(max_length=64, verbose_name="工作空间id", default="default", db_index=True)
    parent = TreeForeignKey("self", on_delete=models.DO_NOTHING, null=True, blank=True, related_name="children")

    class Meta:
        db_table = "knowledge_folder"

    class MPTTMeta:
        order_insertion_by = ["name"]


class Knowledge(AppModelMixin):
    """
    知识库表
    """

    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    name = models.CharField(max_length=150, verbose_name="知识库名称", db_index=True)
    workspace_id = models.CharField(max_length=64, verbose_name="工作空间id", default="default", db_index=True)
    desc = models.CharField(max_length=256, verbose_name="描述")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, db_constraint=False, blank=True, null=True)
    type = models.IntegerField(
        verbose_name="类型", choices=KnowledgeType.choices, default=KnowledgeType.BASE, db_index=True
    )
    scope = models.CharField(
        max_length=20,
        verbose_name="可用范围",
        choices=KnowledgeScope.choices,
        default=KnowledgeScope.WORKSPACE,
        db_index=True,
    )
    folder = models.ForeignKey(KnowledgeFolder, on_delete=models.DO_NOTHING, verbose_name="文件夹id", default="default")
    embedding_model = models.ForeignKey(Model, on_delete=models.SET_NULL, db_constraint=False, blank=True, null=True)
    file_size_limit = models.IntegerField(verbose_name="文件大小限制", default=100)
    file_count_limit = models.IntegerField(verbose_name="文件数量限制", default=50)
    meta = models.JSONField(verbose_name="元数据", default=dict)

    class Meta:
        db_table = "knowledge"


class KnowledgeSyncLog(AppModelMixin):
    """Execution history for manual and scheduled external knowledge synchronization."""

    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    knowledge = models.ForeignKey(
        Knowledge,
        on_delete=models.CASCADE,
        db_constraint=False,
        related_name="sync_logs",
        verbose_name="知识库",
    )
    workspace_id = models.CharField(max_length=64, verbose_name="工作空间id", db_index=True)
    sync_type = models.CharField(
        max_length=16,
        choices=KnowledgeSyncType.choices,
        default=KnowledgeSyncType.INCREMENTAL,
        verbose_name="同步方式",
    )
    trigger_type = models.CharField(
        max_length=16,
        choices=KnowledgeSyncTrigger.choices,
        default=KnowledgeSyncTrigger.MANUAL,
        verbose_name="触发方式",
    )
    status = models.CharField(
        max_length=16,
        choices=KnowledgeSyncStatus.choices,
        default=KnowledgeSyncStatus.RUNNING,
        db_index=True,
        verbose_name="同步状态",
    )
    total_count = models.PositiveIntegerField(default=0, verbose_name="文档总数")
    synced_count = models.PositiveIntegerField(default=0, verbose_name="已同步数")
    skipped_count = models.PositiveIntegerField(default=0, verbose_name="跳过数")
    deleted_count = models.PositiveIntegerField(default=0, verbose_name="删除数")
    failed_count = models.PositiveIntegerField(default=0, verbose_name="失败数")
    duration_ms = models.PositiveBigIntegerField(default=0, verbose_name="耗时毫秒")
    message = models.TextField(default="", blank=True, verbose_name="结果信息")

    class Meta:
        db_table = "knowledge_sync_log"
        ordering = ["-create_time"]
        indexes = [models.Index(fields=["knowledge", "-create_time"])]


class KnowledgeWorkflow(AppModelMixin):
    """
    知识库工作流表
    """

    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    knowledge = models.OneToOneField(
        Knowledge, on_delete=models.CASCADE, verbose_name="知识库", db_constraint=False, related_name="workflow"
    )
    workspace_id = models.CharField(max_length=64, verbose_name="工作空间id", default="default", db_index=True)
    work_flow = models.JSONField(verbose_name="工作流数据", default=dict)
    is_publish = models.BooleanField(verbose_name="是否发布", default=False, db_index=True)
    publish_time = models.DateTimeField(verbose_name="发布时间", null=True, blank=True)

    class Meta:
        db_table = "knowledge_workflow"


class KnowledgeWorkflowVersion(AppModelMixin):
    """
    知识库工作流版本表 - 记录工作流历史版本
    """

    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    knowledge = models.ForeignKey(Knowledge, on_delete=models.CASCADE, verbose_name="知识库", db_constraint=False)
    workspace_id = models.CharField(max_length=64, verbose_name="工作空间id", default="default", db_index=True)
    name = models.CharField(verbose_name="版本名称", max_length=128, default="")
    work_flow = models.JSONField(verbose_name="工作流数据", default=dict)
    publish_user_id = models.UUIDField(verbose_name="发布者id", max_length=128, default=None, null=True)
    publish_user_name = models.CharField(verbose_name="发布者名称", max_length=128, default="")

    class Meta:
        db_table = "knowledge_workflow_version"


def get_default_status():
    return Status("").__str__()


class Document(AppModelMixin):
    """
    文档表
    """

    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    knowledge = models.ForeignKey(Knowledge, on_delete=models.DO_NOTHING, verbose_name="知识库id")
    name = models.CharField(max_length=150, verbose_name="文档名称", db_index=True)
    char_length = models.IntegerField(verbose_name="文档字符数 冗余字段")
    status = models.CharField(verbose_name="状态", max_length=20, default=get_default_status, db_index=True)
    status_meta = models.JSONField(verbose_name="状态统计数据", default=default_status_meta)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, db_constraint=False, blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)
    type = models.IntegerField(
        verbose_name="类型", choices=KnowledgeType.choices, default=KnowledgeType.BASE, db_index=True
    )
    resource_type = models.CharField(
        verbose_name="资源类型",
        max_length=16,
        choices=DocumentResourceType.choices,
        default=DocumentResourceType.DOCUMENT,
        db_index=True,
    )
    hit_handling_method = models.CharField(
        verbose_name="命中处理方式",
        max_length=20,
        choices=HitHandlingMethod.choices,
        default=HitHandlingMethod.optimization,
    )
    directly_return_similarity = models.FloatField(verbose_name="直接回答相似度", default=0.9)
    hit_num = models.IntegerField(verbose_name="召回次数", default=0, db_index=True)
    last_hit_time = models.DateTimeField(verbose_name="最后一次召回时间", null=True, blank=True, db_index=True)

    # 导入/同步策略必须跟随文档保存，后续同步使用同一份策略，避免重新分段造成全量抖动。
    doc_strategy = models.JSONField(verbose_name="文档处理策略", default=dict)
    source_hash = models.CharField(verbose_name="远端文档内容哈希", max_length=64, default="", db_index=True)
    split_strategy_hash = models.CharField(verbose_name="分段策略哈希", max_length=64, default="")
    visual_strategy_hash = models.CharField(verbose_name="图片处理策略哈希", max_length=64, default="")
    index_strategy_hash = models.CharField(verbose_name="索引增强策略哈希", max_length=64, default="")
    sync_version = models.PositiveIntegerField(verbose_name="同步版本", default=0)
    last_sync_time = models.DateTimeField(verbose_name="最后同步时间", null=True, blank=True, db_index=True)

    meta = models.JSONField(verbose_name="元数据", default=dict)

    class Meta:
        db_table = "document"


class Tag(AppModelMixin):
    """
    标签表 - 存储标签的key-value定义
    """

    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    knowledge = models.ForeignKey(Knowledge, on_delete=models.DO_NOTHING, verbose_name="知识库", db_constraint=False)
    key = models.CharField(max_length=64, verbose_name="标签键", db_index=True)
    value = models.CharField(max_length=128, verbose_name="标签值", db_index=True)

    class Meta:
        db_table = "tag"
        unique_together = [["knowledge", "key", "value"]]  # 在同一知识库内key-value组合唯一
        indexes = [
            models.Index(fields=["knowledge", "key"]),
        ]


class DocumentTag(AppModelMixin):
    """
    文档标签关联表
    """

    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    document = models.ForeignKey(Document, on_delete=models.DO_NOTHING, verbose_name="文档", db_constraint=False)
    tag = models.ForeignKey(Tag, on_delete=models.DO_NOTHING, verbose_name="标签", db_constraint=False)

    class Meta:
        db_table = "document_tag"
        unique_together = [["document", "tag"]]  # 文档和标签的组合唯一


class Paragraph(AppModelMixin):
    """
    段落表
    """

    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    document = models.ForeignKey(Document, on_delete=models.DO_NOTHING, db_constraint=False)
    knowledge = models.ForeignKey(Knowledge, on_delete=models.DO_NOTHING)
    content = models.CharField(max_length=102400, verbose_name="段落内容")
    title = models.CharField(max_length=256, verbose_name="标题", default="", db_index=True)
    status = models.CharField(verbose_name="状态", max_length=20, default=get_default_status, db_index=True)
    status_meta = models.JSONField(verbose_name="状态数据", default=default_status_meta)
    hit_num = models.IntegerField(verbose_name="召回次数", default=0, db_index=True)
    last_hit_time = models.DateTimeField(verbose_name="最后一次召回时间", null=True, blank=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    position = models.IntegerField(verbose_name="段落顺序", default=0, db_index=True)
    chunks = ArrayField(verbose_name="块", base_field=models.CharField(), default=list)
    content_schema = models.JSONField(verbose_name="结构化内容", default=list)
    origin = models.CharField(
        verbose_name="内容来源",
        max_length=16,
        choices=ContentOrigin.choices,
        default=ContentOrigin.MANUAL,
        db_index=True,
    )
    source_key = models.CharField(verbose_name="远端稳定键", max_length=512, default="", db_index=True)
    source_hash = models.CharField(verbose_name="远端内容哈希", max_length=64, default="", db_index=True)
    source_snapshot = models.JSONField(verbose_name="上次同步快照", default=dict)
    source_updated_at = models.DateTimeField(verbose_name="远端更新时间", null=True, blank=True)
    local_state = models.CharField(
        verbose_name="本地状态", max_length=16, choices=LocalState.choices, default=LocalState.CLEAN, db_index=True
    )
    sync_state = models.CharField(
        verbose_name="同步状态", max_length=24, choices=SyncState.choices, default=SyncState.ACTIVE, db_index=True
    )
    anchor_paragraph = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        db_constraint=False,
        blank=True,
        null=True,
        related_name="anchored_paragraphs",
    )
    placement = models.CharField(verbose_name="相对锚点位置", max_length=8, default="after")

    class Meta:
        db_table = "paragraph"
        constraints = [
            models.UniqueConstraint(
                fields=["document", "source_key"],
                condition=~models.Q(source_key=""),
                name="uniq_document_paragraph_source_key",
            )
        ]


class ParagraphAsset(AppModelMixin):
    """段落内的图片等资产；资产属于文档生命周期，不是独立知识类型。"""

    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    knowledge = models.ForeignKey(Knowledge, on_delete=models.DO_NOTHING, db_constraint=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, db_constraint=False, related_name="assets")
    paragraph = models.ForeignKey(Paragraph, on_delete=models.CASCADE, db_constraint=False, related_name="assets")
    file = models.ForeignKey("File", on_delete=models.DO_NOTHING, db_constraint=False, related_name="paragraph_assets")
    asset_type = models.CharField(verbose_name="资产类型", max_length=16, default="image", db_index=True)
    position = models.PositiveIntegerField(verbose_name="段落内位置", default=0)
    origin = models.CharField(
        verbose_name="内容来源", max_length=16, choices=ContentOrigin.choices, default=ContentOrigin.SYNCED
    )
    source_asset_key = models.CharField(verbose_name="远端资产稳定键", max_length=512, default="", db_index=True)
    source_hash = models.CharField(verbose_name="远端资产哈希", max_length=64, default="", db_index=True)
    caption = models.TextField(verbose_name="图片标题", default="")
    ocr_text = models.TextField(verbose_name="OCR 文本", default="")
    description = models.TextField(verbose_name="图片描述", default="")
    hit_num = models.IntegerField(verbose_name="召回次数", default=0, db_index=True)
    last_hit_time = models.DateTimeField(verbose_name="最后一次召回时间", null=True, blank=True, db_index=True)
    local_state = models.CharField(
        verbose_name="本地状态", max_length=16, choices=LocalState.choices, default=LocalState.CLEAN
    )
    sync_state = models.CharField(
        verbose_name="同步状态", max_length=24, choices=SyncState.choices, default=SyncState.ACTIVE
    )
    process_status = models.CharField(
        verbose_name="处理状态", max_length=16, choices=AssetProcessStatus.choices, default=AssetProcessStatus.PENDING
    )
    process_error = models.TextField(verbose_name="处理错误", default="")
    visual_strategy_hash = models.CharField(verbose_name="图片处理策略哈希", max_length=64, default="")
    meta = models.JSONField(verbose_name="元数据", default=dict)

    class Meta:
        db_table = "paragraph_asset"
        constraints = [
            models.UniqueConstraint(
                fields=["document", "source_asset_key"],
                condition=~models.Q(source_asset_key=""),
                name="uniq_document_asset_source_key",
            )
        ]


class Problem(AppModelMixin):
    """
    问题表
    """

    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    knowledge = models.ForeignKey(Knowledge, on_delete=models.DO_NOTHING, db_constraint=False)
    content = models.CharField(max_length=256, verbose_name="问题内容", db_index=True)
    hit_num = models.IntegerField(verbose_name="召回次数", default=0, db_index=True)
    last_hit_time = models.DateTimeField(verbose_name="最后一次召回时间", null=True, blank=True, db_index=True)

    class Meta:
        db_table = "problem"


class ProblemParagraphMapping(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    knowledge = models.ForeignKey(Knowledge, on_delete=models.DO_NOTHING, db_constraint=False)
    document = models.ForeignKey(Document, on_delete=models.DO_NOTHING, db_constraint=False)
    problem = models.ForeignKey(Problem, on_delete=models.DO_NOTHING, db_constraint=False)
    paragraph = models.ForeignKey(Paragraph, on_delete=models.DO_NOTHING, db_constraint=False)
    meta = models.JSONField(verbose_name="元数据", default=dict)

    class Meta:
        db_table = "problem_paragraph_mapping"


class Termbase(AppModelMixin):
    """
    术语表
    """

    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    knowledge = models.ForeignKey(Knowledge, on_delete=models.DO_NOTHING, db_constraint=False)
    content = models.CharField(max_length=256, verbose_name="术语内容", db_index=True)

    class Meta:
        db_table = "termbase"


class SourceType(models.IntegerChoices):
    """订单类型"""

    PROBLEM = 0, "问题"
    PARAGRAPH = 1, "段落"
    TITLE = 2, "标题"
    IMAGE = 3, "图片"


class SearchMode(models.TextChoices):
    embedding = "embedding"
    keywords = "keywords"
    blend = "blend"


class FileSourceType(models.TextChoices):
    # 知识库  跟随知识库被删除而被删除 source_id 为知识库id
    KNOWLEDGE = "KNOWLEDGE"
    # 应用  跟随应用被删除而被删除 source_id 为应用id
    APPLICATION = "APPLICATION"
    # 工具  跟随工具被删除而被删除 source_id 为应用id
    TOOL = "TOOL"
    # 文档
    DOCUMENT = "DOCUMENT"
    # 对话
    CHAT = "CHAT"
    SYSTEM = "SYSTEM"
    # 临时30分钟 数据30分钟后被清理 source_id 为TEMPORARY_30_MINUTE
    TEMPORARY_30_MINUTE = "TEMPORARY_30_MINUTE"
    # 临时120分钟 数据120分钟后被清理 source_id为TEMPORARY_100_MINUTE
    TEMPORARY_120_MINUTE = "TEMPORARY_120_MINUTE"
    # 临时1天 数据1天后被清理 source_id为TEMPORARY_1_DAY
    TEMPORARY_1_DAY = "TEMPORARY_1_DAY"


class VectorField(models.Field):
    def db_type(self, connection):
        return "vector"


class Embedding(models.Model):
    id = models.CharField(max_length=128, primary_key=True, verbose_name="主键id")
    source_id = models.CharField(max_length=128, verbose_name="资源id", db_index=True)
    source_type = models.CharField(
        verbose_name="资源类型", max_length=5, choices=SourceType.choices, default=SourceType.PROBLEM, db_index=True
    )
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
    source_type = models.CharField(
        verbose_name="资源类型",
        choices=FileSourceType,
        default=FileSourceType.TEMPORARY_120_MINUTE.value,
        db_index=True,
    )
    source_id = models.CharField(
        verbose_name="资源id", default=FileSourceType.TEMPORARY_120_MINUTE.value, db_index=True
    )
    loid = models.IntegerField(verbose_name="loid", null=True, blank=True)
    storage_type = models.CharField(max_length=16, default="pg", db_index=True)
    meta = models.JSONField(verbose_name="文件关联数据", default=dict)

    class Meta:
        db_table = "file"

    def save(self, bytea=None, force_insert=False, force_update=False, using=None, update_fields=None):
        if bytea is None:
            raise ValueError("bytea参数不能为空")

        sha256_hash = get_sha256_hash(bytea)
        self.sha256_hash = sha256_hash
        existing_file = QuerySet(File).filter(sha256_hash=sha256_hash).first()
        if existing_file:
            self.loid = existing_file.loid
            self.file_size = existing_file.file_size
            self.storage_type = existing_file.storage_type
            if existing_file.storage_type == "seaweedfs":
                # Point to the canonical S3 key; this file has no object of its own
                canonical_key = existing_file.meta.get("seaweedfs_key", f"files/{existing_file.id}")
                self.meta = {**self.meta, "seaweedfs_key": canonical_key}
            return super().save()

        if is_seaweedfs_enabled():
            self.storage_type = "seaweedfs"
            self.file_size = len(bytea)
            self.loid = None
            self.meta = {**self.meta, "seaweedfs_key": f"files/{self.id}"}
            get_s3_client().put_object(Bucket=get_bucket(), Key=f"files/{self.id}", Body=bytea)
        else:
            self.storage_type = "pg"
            compressed_data = self._compress_data(bytea)
            self.file_size = len(compressed_data)
            self.loid = self._create_large_object()
            self.meta = {**self.meta, "original_size": len(bytea)}
            self._write_compressed_data(compressed_data)

        return super().save()

    def _compress_data(self, data, compression_level=9):
        """压缩数据到内存"""
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zipinfo = zipfile.ZipInfo(self.file_name)
            zipinfo.compress_type = zipfile.ZIP_DEFLATED
            zip_file.writestr(zipinfo, data, compresslevel=compression_level)

        return buffer.getvalue()

    def _create_large_object(self):
        result = select_one("SELECT lo_creat(-1)::int8 as lo_id;", [])
        return result["lo_id"]

    def _write_compressed_data(self, data, block_size=64 * 1024):
        buffer = io.BytesIO(data)
        offset = 0

        while True:
            chunk = buffer.read(block_size)
            if not chunk:
                break

            offset += len(chunk)
            select_one(
                "SELECT lo_put(%s::oid, %s::bigint, %s::bytea)::VARCHAR;", [self.loid, offset - len(chunk), chunk]
            )

    def get_bytes(self):
        if self.storage_type == "seaweedfs":
            key = self.meta.get("seaweedfs_key", f"files/{self.id}")
            resp = get_s3_client().get_object(Bucket=get_bucket(), Key=key)
            return resp["Body"].read()

        buffer = io.BytesIO()
        for chunk in self.get_bytes_stream():
            buffer.write(chunk)
        data = buffer.getvalue()
        try:
            # 解压数据
            with zipfile.ZipFile(buffer) as zip_file:
                names = [name for name in zip_file.namelist() if not name.endswith("/")]
                if len(names) != 1:
                    return data
                # 用 zip 内实际存储的条目名，避免文件名不匹配
                name = names[0]
                return zip_file.read(name)
        except zipfile.BadZipFile:
            # 如果数据不是zip格式，直接返回原始数据
            return data

    def get_bytes_stream(self, start=0, end=None, chunk_size=64 * 1024):
        if self.storage_type == "seaweedfs":
            key = self.meta.get("seaweedfs_key", f"files/{self.id}")
            kwargs = {}
            byte_range = []
            if start:
                byte_range.append(f"bytes={start}-")
            if end is not None:
                byte_range = [f"bytes={start}-{end - 1}"]
            if byte_range:
                kwargs["Range"] = byte_range[0]
            resp = get_s3_client().get_object(Bucket=get_bucket(), Key=key, **kwargs)
            body = resp["Body"]
            while True:
                chunk = body.read(chunk_size)
                if not chunk:
                    break
                yield chunk
            return

        def _read_with_offset():
            offset = start
            while True:
                read_size = chunk_size
                if end is not None:
                    remaining = end - offset
                    if remaining <= 0:
                        break
                    read_size = min(chunk_size, remaining)
                result = select_one(
                    "SELECT lo_get(%s::oid, %s, %s) as chunk",
                    [self.loid, offset, read_size],
                )
                chunk = result["chunk"] if result else None
                if not chunk:
                    break
                yield chunk
                offset += len(chunk)
                if len(chunk) < chunk_size:
                    break

        yield from _read_with_offset()


@receiver(pre_delete, sender=File)
def on_delete_file(sender, instance, **kwargs):
    if instance.storage_type == "seaweedfs":
        # Deduped references share a key; only delete the S3 object when no other file points to the same key
        key = instance.meta.get("seaweedfs_key", f"files/{instance.id}")
        shared = QuerySet(File).filter(sha256_hash=instance.sha256_hash).exclude(id=instance.id).exists()
        if not shared:
            try:
                get_s3_client().delete_object(Bucket=get_bucket(), Key=key)
            except Exception:
                pass
    else:
        exist = QuerySet(File).filter(loid=instance.loid).exclude(id=instance.id).exists()
        if not exist:
            select_one(f"SELECT lo_unlink({instance.loid})", [])


class PublicFileAccess(AppModelMixin):
    """
    公共文件访问控制表
    记录哪些文件允许公开访问
    """

    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")

    source_type = models.CharField(
        max_length=20,
        choices=[
            ("FILE", "文件"),
            ("APPLICATION", "应用"),
            ("KNOWLEDGE", "知识库"),
        ],
        db_index=True,
        verbose_name="资源类型",
    )
    source_id = models.CharField(max_length=128, db_index=True, verbose_name="资源ID")

    class Meta:
        db_table = "public_file_access"
        indexes = [
            models.Index(fields=["source_type", "source_id"]),
        ]
