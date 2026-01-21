# coding=utf-8
"""
PageIndex节点异步向量化任务
"""
from celery import shared_task
from knowledge.models import PageIndexNode, State
from knowledge.task.embedding import get_embedding_model
from django.db.models import QuerySet, Count
from common.utils.logger import maxkb_logger


@shared_task
def generate_page_index_embeddings(document_id: str):
    """
    异步生成PageIndex节点的嵌入向量

    Args:
        document_id: 文档ID
    """
    from knowledge.models import Document, Knowledge

    document = QuerySet(Document).filter(id=document_id).first()
    if not document:
        maxkb_logger.warning(f'[PageIndex] Document not found: {document_id}')
        return

    knowledge = document.knowledge

    # 获取向量化模型
    embedding_model_id = knowledge.embedding_model_id
    if not embedding_model_id:
        maxkb_logger.warning(f'[PageIndex] No embedding model for knowledge: {knowledge.id}')
        return

    # 获取embedding客户端
    try:
        embedding_client = get_embedding_model(str(embedding_model_id))
    except Exception as e:
        maxkb_logger.error(f'[PageIndex] Failed to get embedding model: {e}')
        return

    # 获取所有待向量化的PageIndex节点
    nodes = QuerySet(PageIndexNode).filter(document=document)

    node_count = nodes.count()
    if node_count == 0:
        maxkb_logger.warning(f'[PageIndex] No PageIndex nodes found for document {document_id}')
        return

    status_summary = list(nodes.values('embedding_status').annotate(count=Count('id')).order_by('embedding_status'))
    maxkb_logger.info(
        f'[PageIndex] Starting embedding generation for {node_count} nodes, status summary: {status_summary}'
    )

    if nodes.exists():
        nodes.update(embedding_status=State.STARTED.value)

    # 批量生成嵌入
    success_count = 0
    for node in nodes:
        try:
            if len(node.content) == 0:
                QuerySet(PageIndexNode).filter(id=node.id).update(embedding_status=State.IGNORED.value)
                continue

            content = node.content
            if len(content) > 2048:
                maxkb_logger.warning(
                    f'[PageIndex] Node content too long ({len(content)}), truncate to 2048: {node.id}'
                )
                content = content[:2048]

            # 生成嵌入向量
            embedding = embedding_client.embed_query(content)

            # 更新节点的embedding字段（通过SQL直接更新）
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE page_index_node SET embedding = %s::vector, embedding_status = %s WHERE id = %s",
                    (str(embedding), State.SUCCESS.value, str(node.id))
                )
            success_count += 1

        except Exception as e:
            QuerySet(PageIndexNode).filter(id=node.id).update(embedding_status=State.FAILURE.value)
            maxkb_logger.error(f'[PageIndex] Failed to embed node {node.id}: {e}')

    status_summary = list(QuerySet(PageIndexNode).filter(document=document).values(
        'embedding_status'
    ).annotate(count=Count('id')).order_by('embedding_status'))
    maxkb_logger.info(
        f'[PageIndex] Embedding generation completed for document {document_id}: '
        f'{success_count}/{node_count} nodes, status summary: {status_summary}'
    )
