# coding=utf-8
"""
    @project: maxkb
    @Author：AI Assistant
    @file： tag.py
    @date：2025/10/13
    @desc: 标签系统相关序列化器
"""
from collections import defaultdict
from typing import Dict

import uuid_utils.compat as uuid
from django.db import transaction
from django.db.models import QuerySet
from django.db.models.query_utils import Q
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.exception.app_exception import AppApiException
from knowledge.models import Tag, Knowledge, DocumentTag


class TagModelSerializer(serializers.ModelSerializer):
    """标签模型序列化器"""

    class Meta:
        model = Tag
        fields = ['id', 'knowledge_id', 'key', 'value', 'create_time', 'update_time']
        read_only_fields = ['id', 'create_time', 'update_time']


class TagCreateSerializer(serializers.Serializer):
    """创建标签序列化器"""
    key = serializers.CharField(required=True, max_length=64, label=_('Tag Key'))
    value = serializers.CharField(required=True, max_length=128, label=_('Tag Value'))


class TagEditSerializer(serializers.Serializer):
    key = serializers.CharField(required=False, max_length=64, label=_('Tag Key'))
    value = serializers.CharField(required=False, max_length=128, label=_('Tag Value'))


class TagSerializers(serializers.Serializer):
    class Create(serializers.Serializer):
        workspace_id = serializers.CharField(required=True, label=_('Workspace ID'))
        knowledge_id = serializers.UUIDField(required=True, label=_('Knowledge ID'))
        tags = serializers.ListField(required=True, label=_('Tags'), child=TagCreateSerializer())

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            workspace_id = self.data.get('workspace_id')
            query_set = QuerySet(Knowledge).filter(id=self.data.get('knowledge_id'))
            if workspace_id and workspace_id != 'None':
                query_set = query_set.filter(workspace_id=workspace_id)
            if not query_set.exists():
                raise AppApiException(500, _('Knowledge id does not exist'))

        def insert(self):
            self.is_valid(raise_exception=True)

            knowledge_id = self.data.get('knowledge_id')

            # 获取数据库中已存在的key-value组合
            existing_tags = set(
                QuerySet(Tag).filter(knowledge_id=knowledge_id)
                .values_list('key', 'value', named=False)
            )

            # 过滤掉已存在的标签
            tag_objects = []
            for tag_data in self.data.get('tags', []):
                key = tag_data.get('key')
                value = tag_data.get('value')

                # 检查key-value组合是否已存在
                if (key, value) not in existing_tags:
                    tag = Tag(
                        id=uuid.uuid7(),
                        knowledge_id=knowledge_id,
                        key=key,
                        value=value
                    )
                    tag_objects.append(tag)
                    # 将新标签添加到已存在集合中，避免本次批量插入中的重复
                    existing_tags.add((key, value))

            # 批量插入未重复的标签
            if tag_objects:
                Tag.objects.bulk_create(tag_objects)

    class Operate(serializers.Serializer):
        workspace_id = serializers.CharField(required=True, label=_('Workspace ID'))
        knowledge_id = serializers.UUIDField(required=True, label=_('Knowledge ID'))
        tag_id = serializers.UUIDField(required=True, label=_('Tag ID'))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            workspace_id = self.data.get('workspace_id')
            query_set = QuerySet(Knowledge).filter(id=self.data.get('knowledge_id'))
            if workspace_id and workspace_id != 'None':
                query_set = query_set.filter(workspace_id=workspace_id)
            if not query_set.exists():
                raise AppApiException(500, _('Knowledge id does not exist'))

        @transaction.atomic
        def edit(self, instance: Dict):
            self.is_valid(raise_exception=True)
            tag = QuerySet(Tag).get(id=self.data.get('tag_id'))
            if tag is None:
                raise AppApiException(500, _('Tag id does not exist'))

            # 如果key发生变化，更新所有相同key的标签
            if instance.get('key') and instance.get('key') != tag.key:
                old_key = tag.key
                new_key = instance.get('key')

                # 检查新key是否已存在于同一个knowledge中
                existing_key_exists = QuerySet(Tag).filter(
                    knowledge_id=tag.knowledge_id,
                    key=new_key
                ).exists()

                if existing_key_exists:
                    raise AppApiException(500, _('Tag key already exists'))

                # 批量更新所有具有相同old_key的标签
                QuerySet(Tag).filter(
                    knowledge_id=tag.knowledge_id,
                    key=old_key
                ).update(key=new_key)

            # 如果只是value变化，只更新当前标签
            if instance.get('value') and instance.get('value') != tag.value:
                # 检查新key是否已存在于同一个knowledge中
                existing_value_exists = QuerySet(Tag).filter(
                    knowledge_id=tag.knowledge_id,
                    key=instance.get('key'),
                    value=instance.get('value')
                ).exists()

                if existing_value_exists:
                    raise AppApiException(500, _('Tag value already exists'))
                QuerySet(Tag).filter(
                    id=tag.id
                ).update(value=instance.get('value'))

        @transaction.atomic
        def delete(self, delete_type: str):
            self.is_valid(raise_exception=True)
            if delete_type == 'key':
                # 删除同一knowledge_id下相同key的所有标签
                tag = QuerySet(Tag).get(id=self.data.get('tag_id'))
                if tag is None:
                    raise AppApiException(500, _('Tag id does not exist'))
                QuerySet(Tag).filter(
                    knowledge_id=tag.knowledge_id,
                    key=tag.key
                ).delete()
                QuerySet(DocumentTag).filter(tag_id=tag.id).delete()
            else:
                # 仅删除当前标签
                QuerySet(Tag).filter(id=self.data.get('tag_id')).delete()
                QuerySet(DocumentTag).filter(tag_id=self.data.get('tag_id')).delete()

    class BatchDelete(serializers.Serializer):
        workspace_id = serializers.CharField(required=True, label=_('Workspace ID'))
        knowledge_id = serializers.UUIDField(required=True, label=_('Knowledge ID'))
        tag_ids = serializers.ListField(required=True, label=_('Tag IDs'), child=serializers.UUIDField())

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            workspace_id = self.data.get('workspace_id')
            query_set = QuerySet(Knowledge).filter(id=self.data.get('knowledge_id'))
            if workspace_id and workspace_id != 'None':
                query_set = query_set.filter(workspace_id=workspace_id)
            if not query_set.exists():
                raise AppApiException(500, _('Knowledge id does not exist'))

        @transaction.atomic
        def batch_delete(self):
            self.is_valid(raise_exception=True)
            tag_ids = self.data.get('tag_ids', [])
            if not tag_ids:
                return

            # 获取要删除的标签的key
            tags_to_delete = QuerySet(Tag).filter(id__in=tag_ids)
            keys_to_delete = set(tags_to_delete.values_list('key', flat=True))

            # 删除具有相同key的所有标签
            QuerySet(Tag).filter(
                knowledge_id=self.data.get('knowledge_id'),
                key__in=keys_to_delete
            ).delete()

            # 删除关联的DocumentTag
            QuerySet(DocumentTag).filter(tag_id__in=tag_ids).delete()

    class Query(serializers.Serializer):
        workspace_id = serializers.CharField(required=True, label=_('Workspace ID'))
        knowledge_id = serializers.UUIDField(required=True, label=_('Knowledge ID'))
        name = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('search value'))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            workspace_id = self.data.get('workspace_id')
            query_set = QuerySet(Knowledge).filter(id=self.data.get('knowledge_id'))
            if workspace_id and workspace_id != 'None':
                query_set = query_set.filter(workspace_id=workspace_id)
            if not query_set.exists():
                raise AppApiException(500, _('Knowledge id does not exist'))

        def list(self):
            self.is_valid(raise_exception=True)
            if self.data.get('name'):
                name = self.data.get('name')
                tags = QuerySet(Tag).filter(
                    knowledge_id=self.data.get('knowledge_id')
                ).filter(
                    Q(key__icontains=name) | Q(value__icontains=name)
                ).values('key', 'value', 'id', 'create_time', 'update_time').order_by('create_time', 'key', 'value')
            else:
                # 获取所有标签，按创建时间排序保持稳定顺序
                tags = QuerySet(Tag).filter(
                    knowledge_id=self.data.get('knowledge_id')
                ).values('key', 'value', 'id', 'create_time', 'update_time').order_by('create_time', 'key', 'value')

            # 按key分组
            grouped_tags = defaultdict(list)
            for tag in tags:
                grouped_tags[tag['key']].append({
                    'id': tag['id'],
                    'value': tag['value'],
                    'create_time': tag['create_time'],
                    'update_time': tag['update_time']
                })

            # 转换为期望的格式，保持key的顺序
            result = []
            # 按key排序以确保结果顺序一致
            for key in sorted(grouped_tags.keys()):
                values = grouped_tags[key]
                # 按创建时间对values进行排序
                values.sort(key=lambda x: x['create_time'])
                result.append({
                    'key': key,
                    'values': values,
                })

            return result
