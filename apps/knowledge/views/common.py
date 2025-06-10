from django.db.models import QuerySet

from knowledge.models import Document


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


def get_knowledge_document_operation_object(knowledge_dict: dict, document_dict: dict):
    return {
        'name': f'{knowledge_dict.get("name", "")}/{document_dict.get("name", "")}',
        'dataset_name': knowledge_dict.get("name", ""),
        'dataset_desc': knowledge_dict.get("desc", ""),
        'dataset_type': knowledge_dict.get("type", ""),
        'document_name': document_dict.get("name", ""),
        'document_type': document_dict.get("type", ""),
    }
