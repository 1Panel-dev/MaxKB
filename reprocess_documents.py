#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量重新处理文档脚本
使用方法: python reprocess_documents.py [--batch-size 10] [--knowledge-id xxx]
"""
import sys
import os
import django
import argparse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maxkb.settings')
django.setup()

from knowledge.models import Document, Knowledge
from knowledge.task.embedding import embedding_by_document

def reprocess_documents(knowledge_id=None, batch_size=None):
    """
    重新处理文档
    
    Args:
        knowledge_id: 知识库ID（可选，不指定则处理所有）
        batch_size: 批次大小（可选，不指定则处理所有）
    """
    # 构建查询
    query = Document.objects.filter(status='SUCCESS')
    if knowledge_id:
        query = query.filter(knowledge_id=knowledge_id)
    
    # 限制批次大小
    if batch_size:
        docs = query[:batch_size]
        total = batch_size
    else:
        docs = query
        total = query.count()
    
    print(f"📊 准备重新处理 {total} 个文档...")
    
    processed = 0
    for doc in docs:
        try:
            print(f"[{processed+1}/{total}] 处理文档: {doc.name}")
            embedding_by_document.delay(
                str(doc.id),
                str(doc.knowledge.embedding_model_id)
            )
            processed += 1
        except Exception as e:
            print(f"  ❌ 失败: {str(e)}")
    
    print(f"\n✅ 已提交 {processed} 个文档到处理队列")
    print("⏳ 请等待后台任务完成...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='批量重新处理文档')
    parser.add_argument('--batch-size', type=int, help='每批处理的文档数量')
    parser.add_argument('--knowledge-id', type=str, help='指定知识库ID')
    parser.add_argument('--list', action='store_true', help='列出所有知识库')
    
    args = parser.parse_args()
    
    if args.list:
        print("\n📚 所有知识库列表:")
        print("-" * 80)
        for kb in Knowledge.objects.all():
            doc_count = Document.objects.filter(
                knowledge_id=kb.id,
                status='SUCCESS'
            ).count()
            print(f"{kb.name}")
            print(f"  ID: {kb.id}")
            print(f"  文档数: {doc_count}")
            print("-" * 80)
    else:
        reprocess_documents(args.knowledge_id, args.batch_size)

