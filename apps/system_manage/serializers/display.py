# coding=utf-8
"""
    @project: maxkb
    @file: display.py
    @desc: 外观/白标设置序列化器。

    数据存放：
      - 配置 JSON 落在 SystemSetting(type=THEME).meta
      - 上传图片落在 knowledge.File（source_type=SYSTEM, source_id='THEME'），
        URL 形式为 "./oss/file/<uuid>"，由 oss.FileRetrievalView 公开访问，
        登录页（未认证）也能正常渲染。
"""
import uuid_utils.compat as uuid
from django.core.files.uploadedfile import UploadedFile
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.exception.app_exception import AppApiException
from knowledge.models import File, FileSourceType
from system_manage.models import SystemSetting, SettingType

# 图片字段统一处理
IMAGE_FIELDS = ('icon', 'loginLogo', 'loginImage')

# 允许的图片扩展名（与前端 accept 一致）
ALLOWED_IMAGE_EXT = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp')

# 单张图片大小上限（10 MB，与前端 onChange 校验一致）
MAX_IMAGE_SIZE = 10 * 1024 * 1024

# 系统 THEME 资源在 File 表的 source_id 常量
THEME_SOURCE_ID = 'THEME'

# 默认配置：首次安装、尚未保存过 THEME 记录时返回给前端
DEFAULTS = {
    'theme': '#3370FF',
    'icon': '',
    'loginLogo': '',
    'loginImage': '',
    'title': 'MaxKB',
    'slogan': '',
    'showUserManual': True,
    'userManualUrl': '',
    'showForum': True,
    'forumUrl': '',
    'showProject': True,
    'projectUrl': '',
}


def _save_image_file(uploaded: UploadedFile) -> str:
    """把上传文件落到 File 表，返回 './oss/file/<uuid>' 形式的相对 URL。"""
    name = (uploaded.name or '').lower()
    ext = '.' + name.rsplit('.', 1)[-1] if '.' in name else ''
    if ext not in ALLOWED_IMAGE_EXT:
        raise AppApiException(500, _('Unsupported image format'))
    if uploaded.size and uploaded.size > MAX_IMAGE_SIZE:
        raise AppApiException(500, _('Image size exceeds limit'))

    file_id = uuid.uuid7()
    file = File(
        id=file_id,
        file_name=uploaded.name,
        source_type=FileSourceType.SYSTEM.value,
        source_id=THEME_SOURCE_ID,
        meta={'usage': 'display'},
    )
    file.save(uploaded.read())
    return f'./oss/file/{file_id}'


def _maybe_delete_old_image(url: str):
    """旧图片已被替换或清空时，尽力删除 File 记录（失败不致命）。"""
    if not url or not isinstance(url, str):
        return
    if '/oss/file/' not in url:
        return
    try:
        file_id = url.rstrip('/').rsplit('/', 1)[-1]
        old = QuerySet(File).filter(id=file_id, source_id=THEME_SOURCE_ID).first()
        if old is not None:
            old.delete()
    except Exception:
        # 孤儿图片清理是 best-effort，失败不要打断保存
        pass


class DisplayInfoSerializer(serializers.Serializer):
    """外观设置入口。统一对外只暴露 one() 和 Create.update_or_save()，与 EmailSettingSerializer 风格一致。"""

    @staticmethod
    def one():
        record = QuerySet(SystemSetting).filter(type=SettingType.THEME.value).first()
        merged = dict(DEFAULTS)
        if record is not None and isinstance(record.meta, dict):
            # 已存配置覆盖默认；后续如果加新字段，老记录会自动用 DEFAULTS 填充
            for k, v in record.meta.items():
                merged[k] = v
        return merged

    class Create(serializers.Serializer):
        # 非图片字段
        theme = serializers.CharField(required=False, allow_blank=True, max_length=32)
        title = serializers.CharField(required=False, allow_blank=True, max_length=128)
        slogan = serializers.CharField(required=False, allow_blank=True, max_length=64)
        showUserManual = serializers.BooleanField(required=False)
        userManualUrl = serializers.CharField(required=False, allow_blank=True, max_length=128)
        showForum = serializers.BooleanField(required=False)
        forumUrl = serializers.CharField(required=False, allow_blank=True, max_length=128)
        showProject = serializers.BooleanField(required=False)
        projectUrl = serializers.CharField(required=False, allow_blank=True, max_length=128)
        # 图片字段：可能是 UploadedFile（新上传）/ str（保留旧 URL）/ ''（清空）
        # DRF 序列化器不容易直接表达这种"多型"字段，因此在 update_or_save 里走 initial_data 自行处理。

        def update_or_save(self):
            self.is_valid(raise_exception=True)

            previous = DisplayInfoSerializer.one()

            new_meta = dict(previous)  # 以旧配置打底，未传字段保留原值

            # 1) 非图片字段：以本次提交为准
            for key in (
                'theme', 'title', 'slogan',
                'showUserManual', 'userManualUrl',
                'showForum', 'forumUrl',
                'showProject', 'projectUrl',
            ):
                if key in self.validated_data:
                    new_meta[key] = self.validated_data[key]

            # 2) 图片字段：从 initial_data 取原始值
            raw = self.initial_data or {}
            for field in IMAGE_FIELDS:
                if field not in raw:
                    continue
                value = raw.get(field)
                old_url = previous.get(field) or ''
                if isinstance(value, UploadedFile):
                    # 替换：先存新，再删旧
                    new_meta[field] = _save_image_file(value)
                    if old_url and old_url != new_meta[field]:
                        _maybe_delete_old_image(old_url)
                elif isinstance(value, str):
                    # 字符串：可能是空（清空恢复默认）或旧 URL（不变）
                    if value == '':
                        if old_url:
                            _maybe_delete_old_image(old_url)
                        new_meta[field] = ''
                    else:
                        # 保留原 URL；前端传回什么后端就尊重什么（同 URL 等价于不变）
                        new_meta[field] = value
                # 其他类型（None / 异常对象）静默忽略，保留旧值

            # 3) 持久化
            record = QuerySet(SystemSetting).filter(type=SettingType.THEME.value).first()
            if record is None:
                record = SystemSetting(type=SettingType.THEME.value)
            record.meta = new_meta
            record.save()
            return new_meta
