# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： model_apply_serializers.py
    @date：2024/8/20 20:39
    @desc:
"""
import json
import threading
import time

from django.db import connection
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from langchain_core.documents import Document
from rest_framework import serializers

from local_model.models import Model
from local_model.serializers.rsa_util import rsa_long_decrypt
from models_provider.impl.local_model_provider.local_model_provider import LocalModelProvider

from common.cache.mem_cache import MemCache

_lock = threading.Lock()
locks = {}


class ModelManage:
    cache = MemCache('model', {})
    up_clear_time = time.time()

    @staticmethod
    def _get_lock(_id):
        lock = locks.get(_id)
        if lock is None:
            with _lock:
                lock = locks.get(_id)
                if lock is None:
                    lock = threading.Lock()
                    locks[_id] = lock

        return lock

    @staticmethod
    def get_model(_id, get_model):
        model_instance = ModelManage.cache.get(_id)
        if model_instance is None:
            lock = ModelManage._get_lock(_id)
            with lock:
                model_instance = ModelManage.cache.get(_id)
                if model_instance is None:
                    model_instance = get_model(_id)
                    ModelManage.cache.set(_id, model_instance, timeout=60 * 60 * 8)
        else:
            if model_instance.is_cache_model():
                ModelManage.cache.touch(_id, timeout=60 * 60 * 8)
            else:
                model_instance = get_model(_id)
                ModelManage.cache.set(_id, model_instance, timeout=60 * 60 * 8)
        ModelManage.clear_timeout_cache()
        return model_instance

    @staticmethod
    def clear_timeout_cache():
        if time.time() - ModelManage.up_clear_time > 60 * 60:
            threading.Thread(target=lambda: ModelManage.cache.clear_timeout_data()).start()
            ModelManage.up_clear_time = time.time()

    @staticmethod
    def delete_key(_id):
        if ModelManage.cache.has_key(_id):
            ModelManage.cache.delete(_id)


def get_local_model(model, **kwargs):
    return LocalModelProvider().get_model(model.model_type, model.model_name,
                                          json.loads(
                                              rsa_long_decrypt(model.credential)),
                                          model_id=model.id,
                                          streaming=True, **kwargs)


def get_embedding_model(model_id):
    model = QuerySet(Model).filter(id=model_id).first()
    # 手动关闭数据库连接
    connection.close()
    embedding_model = ModelManage.get_model(model_id,
                                            lambda _id: get_local_model(model, use_local=True))
    return embedding_model


class EmbedDocuments(serializers.Serializer):
    texts = serializers.ListField(required=True, child=serializers.CharField(required=True,
                                                                             label=_('vector text')),
                                  label=_('vector text list')),


class EmbedQuery(serializers.Serializer):
    text = serializers.CharField(required=True, label=_('vector text'))


class CompressDocument(serializers.Serializer):
    page_content = serializers.CharField(required=True, label=_('text'))
    metadata = serializers.DictField(required=False, label=_('metadata'))


class CompressDocuments(serializers.Serializer):
    documents = CompressDocument(required=True, many=True)
    query = serializers.CharField(required=True, label=_('query'))


class ValidateModelSerializers(serializers.Serializer):
    model_name = serializers.CharField(required=True, label=_('model_name'))

    model_type = serializers.CharField(required=True, label=_('model_type'))

    model_credential = serializers.DictField(required=True, label="credential")

    def validate_model(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        LocalModelProvider().is_valid_credential(self.data.get('model_type'), self.data.get('model_name'),
                                                 self.data.get('model_credential'), model_params={},
                                                 raise_exception=True)


class ModelApplySerializers(serializers.Serializer):
    model_id = serializers.UUIDField(required=True, label=_('model id'))

    def embed_documents(self, instance, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
            EmbedDocuments(data=instance).is_valid(raise_exception=True)

        model = get_embedding_model(self.data.get('model_id'))
        return model.embed_documents(instance.getlist('texts'))

    def embed_query(self, instance, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
            EmbedQuery(data=instance).is_valid(raise_exception=True)

        model = get_embedding_model(self.data.get('model_id'))
        return model.embed_query(instance.get('text'))

    def compress_documents(self, instance, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
            CompressDocuments(data=instance).is_valid(raise_exception=True)
        model = get_embedding_model(self.data.get('model_id'))
        return [{'page_content': d.page_content, 'metadata': d.metadata} for d in model.compress_documents(
            [Document(page_content=document.get('page_content'), metadata=document.get('metadata')) for document in
             instance.get('documents')], instance.get('query'))]

    def unload(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        ModelManage.delete_key(self.data.get('model_id'))
        return True
