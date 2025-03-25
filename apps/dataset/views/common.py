# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： common.py.py
    @date：2025/3/25 15:43
    @desc:
"""
from django.db.models import QuerySet

from dataset.models import DataSet, Document


def get_dataset_operation_object(dataset_id: str):
    dataset_model = QuerySet(model=DataSet).filter(id=dataset_id).first()
    if dataset_model is not None:
        return {
            "name": dataset_model.name,
            "desc": dataset_model.desc,
            "type": dataset_model.type,
            "create_time": dataset_model.create_time,
            "update_time": dataset_model.update_time
        }
    return {}


def get_document_operation_object(document_id: str):
    document_model = QuerySet(model=Document).filter(id=document_id).first()
    if document_model is not None:
        return {
            "name": document_model.name,
            "type": document_model.type,
        }
    return {}


def get_document_operation_object_batch(document_id_list: str):
    document_model_list = QuerySet(model=Document).filter(id__in=document_id_list)
    if document_model_list is not None:
        return {
            "name": f'[{",".join([document_model.name for document_model in document_model_list])}]',
            'document_list': [{'name': document_model.name, 'type': document_model.type} for document_model in
                              document_model_list]
        }
    return {}


def get_dataset_document_operation_object(dataset_dict: dict, document_dict: dict):
    return {
        'name': f'{dataset_dict.get("name", "")}/{document_dict.get("name", "")}',
        'dataset_name': dataset_dict.get("name", ""),
        'dataset_desc': dataset_dict.get("desc", ""),
        'dataset_type': dataset_dict.get("type", ""),
        'document_name': document_dict.get("name", ""),
        'document_type': document_dict.get("type", ""),
    }
