# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： common_serializers.py
    @date：2023/11/17 11:00
    @desc:
"""
import os
import re
import uuid
import zipfile
from typing import List

from django.db.models import QuerySet
from drf_yasg import openapi
from rest_framework import serializers

from common.config.embedding_config import ModelManage
from common.db.search import native_search
from common.db.sql_execute import update_execute
from common.exception.app_exception import AppApiException
from common.mixins.api_mixin import ApiMixin
from common.util.field_message import ErrMessage
from common.util.file_util import get_file_content
from common.util.fork import Fork
from dataset.models import Paragraph, Problem, ProblemParagraphMapping, DataSet, File, Image
from setting.models_provider import get_model
from smartdoc.conf import PROJECT_DIR
from django.utils.translation import gettext_lazy as _


def zip_dir(zip_path, output=None):
    output = output or os.path.basename(zip_path) + '.zip'
    zip = zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(zip_path):
        relative_root = '' if root == zip_path else root.replace(zip_path, '') + os.sep
        for filename in files:
            zip.write(os.path.join(root, filename), relative_root + filename)
    zip.close()


def is_valid_uuid(s):
    try:
        uuid.UUID(s)
        return True
    except ValueError:
        return False


def write_image(zip_path: str, image_list: List[str]):
    for image in image_list:
        search = re.search("\(.*\)", image)
        if search:
            text = search.group()
            if text.startswith('(/api/file/'):
                r = text.replace('(/api/file/', '').replace(')', '')
                r = r.strip().split(" ")[0]
                if not is_valid_uuid(r):
                    break
                file = QuerySet(File).filter(id=r).first()
                if file is None:
                    break
                zip_inner_path = os.path.join('api', 'file', r)
                file_path = os.path.join(zip_path, zip_inner_path)
                if not os.path.exists(os.path.dirname(file_path)):
                    os.makedirs(os.path.dirname(file_path))
                with open(os.path.join(zip_path, file_path), 'wb') as f:
                    f.write(file.get_byte())
            else:
                r = text.replace('(/api/image/', '').replace(')', '')
                r = r.strip().split(" ")[0]
                if not is_valid_uuid(r):
                    break
                image_model = QuerySet(Image).filter(id=r).first()
                if image_model is None:
                    break
                zip_inner_path = os.path.join('api', 'image', r)
                file_path = os.path.join(zip_path, zip_inner_path)
                if not os.path.exists(os.path.dirname(file_path)):
                    os.makedirs(os.path.dirname(file_path))
                with open(file_path, 'wb') as f:
                    f.write(image_model.image)


def update_document_char_length(document_id: str):
    update_execute(get_file_content(
        os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'update_document_char_length.sql')),
        (document_id, document_id))


def list_paragraph(paragraph_list: List[str]):
    if paragraph_list is None or len(paragraph_list) == 0:
        return []
    return native_search(QuerySet(Paragraph).filter(id__in=paragraph_list), get_file_content(
        os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'list_paragraph.sql')))


class MetaSerializer(serializers.Serializer):
    class WebMeta(serializers.Serializer):
        source_url = serializers.CharField(required=True, error_messages=ErrMessage.char(_('source url')))
        selector = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                         error_messages=ErrMessage.char(_('selector')))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            source_url = self.data.get('source_url')
            response = Fork(source_url, []).fork()
            if response.status == 500:
                raise AppApiException(500, _('URL error, cannot parse [{source_url}]').format(source_url=source_url))

    class BaseMeta(serializers.Serializer):
        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)


class BatchSerializer(ApiMixin, serializers.Serializer):
    id_list = serializers.ListField(required=True, child=serializers.UUIDField(required=True),
                                    error_messages=ErrMessage.char(_('id list')))

    def is_valid(self, *, model=None, raise_exception=False):
        super().is_valid(raise_exception=True)
        if model is not None:
            id_list = self.data.get('id_list')
            model_list = QuerySet(model).filter(id__in=id_list)
            if len(model_list) != len(id_list):
                model_id_list = [str(m.id) for m in model_list]
                error_id_list = list(filter(lambda row_id: not model_id_list.__contains__(row_id), id_list))
                raise AppApiException(500, _('The following id does not exist: {error_id_list}').format(
                    error_id_list=error_id_list))

    @staticmethod
    def get_request_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id_list': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING),
                                          title=_('id list'),
                                          description=_('id list'))
            }
        )


class ProblemParagraphObject:
    def __init__(self, dataset_id: str, document_id: str, paragraph_id: str, problem_content: str):
        self.dataset_id = dataset_id
        self.document_id = document_id
        self.paragraph_id = paragraph_id
        self.problem_content = problem_content


def or_get(exists_problem_list, content, dataset_id, document_id, paragraph_id, problem_content_dict):
    if content in problem_content_dict:
        return problem_content_dict.get(content)[0], document_id, paragraph_id
    exists = [row for row in exists_problem_list if row.content == content]
    if len(exists) > 0:
        problem_content_dict[content] = exists[0], False
        return exists[0], document_id, paragraph_id
    else:
        problem = Problem(id=uuid.uuid1(), content=content, dataset_id=dataset_id)
        problem_content_dict[content] = problem, True
        return problem, document_id, paragraph_id


class ProblemParagraphManage:
    def __init__(self, problemParagraphObjectList: [ProblemParagraphObject], dataset_id):
        self.dataset_id = dataset_id
        self.problemParagraphObjectList = problemParagraphObjectList

    def to_problem_model_list(self):
        problem_list = [item.problem_content for item in self.problemParagraphObjectList]
        exists_problem_list = []
        if len(self.problemParagraphObjectList) > 0:
            # 查询到已存在的问题列表
            exists_problem_list = QuerySet(Problem).filter(dataset_id=self.dataset_id,
                                                           content__in=problem_list).all()
        problem_content_dict = {}
        problem_model_list = [
            or_get(exists_problem_list, problemParagraphObject.problem_content, problemParagraphObject.dataset_id,
                   problemParagraphObject.document_id, problemParagraphObject.paragraph_id, problem_content_dict) for
            problemParagraphObject in self.problemParagraphObjectList]

        problem_paragraph_mapping_list = [
            ProblemParagraphMapping(id=uuid.uuid1(), document_id=document_id, problem_id=problem_model.id,
                                    paragraph_id=paragraph_id,
                                    dataset_id=self.dataset_id) for
            problem_model, document_id, paragraph_id in problem_model_list]

        result = [problem_model for problem_model, is_create in problem_content_dict.values() if
                  is_create], problem_paragraph_mapping_list
        return result


def get_embedding_model_by_dataset_id_list(dataset_id_list: List):
    dataset_list = QuerySet(DataSet).filter(id__in=dataset_id_list)
    if len(set([dataset.embedding_mode_id for dataset in dataset_list])) > 1:
        raise Exception(_('The knowledge base is inconsistent with the vector model'))
    if len(dataset_list) == 0:
        raise Exception(_('Knowledge base setting error, please reset the knowledge base'))
    return ModelManage.get_model(str(dataset_list[0].embedding_mode_id),
                                 lambda _id: get_model(dataset_list[0].embedding_mode))


def get_embedding_model_by_dataset_id(dataset_id: str):
    dataset = QuerySet(DataSet).select_related('embedding_mode').filter(id=dataset_id).first()
    return ModelManage.get_model(str(dataset.embedding_mode_id), lambda _id: get_model(dataset.embedding_mode))


def get_embedding_model_by_dataset(dataset):
    return ModelManage.get_model(str(dataset.embedding_mode_id), lambda _id: get_model(dataset.embedding_mode))


def get_embedding_model_id_by_dataset_id(dataset_id):
    dataset = QuerySet(DataSet).select_related('embedding_mode').filter(id=dataset_id).first()
    return str(dataset.embedding_mode_id)


def get_embedding_model_id_by_dataset_id_list(dataset_id_list: List):
    dataset_list = QuerySet(DataSet).filter(id__in=dataset_id_list)
    if len(set([dataset.embedding_mode_id for dataset in dataset_list])) > 1:
        raise Exception(_('The knowledge base is inconsistent with the vector model'))
    if len(dataset_list) == 0:
        raise Exception(_('Knowledge base setting error, please reset the knowledge base'))
    return str(dataset_list[0].embedding_mode_id)


class GenerateRelatedSerializer(ApiMixin, serializers.Serializer):
    model_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_('Model id')))
    prompt = serializers.CharField(required=True, error_messages=ErrMessage.uuid(_('Prompt word')))
    state_list = serializers.ListField(required=False, child=serializers.CharField(required=True),
                                       error_messages=ErrMessage.list("state list"))

    @staticmethod
    def get_request_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'model_id': openapi.Schema(type=openapi.TYPE_STRING,
                                           title=_('Model id'),
                                           description=_('Model id')),
                'prompt': openapi.Schema(type=openapi.TYPE_STRING, title=_('Prompt word'),
                                         description=_("Prompt word")),
                'state_list': openapi.Schema(type=openapi.TYPE_ARRAY,
                                             items=openapi.Schema(type=openapi.TYPE_STRING),
                                             title=_('state list'))
            }
        )
