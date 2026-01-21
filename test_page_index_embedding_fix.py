#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试PageIndex向量化修复
验证点击向量化时，embedding表中的page_index_node_id字段能够正确填充

测试场景：
1. 创建文档和段落
2. 点击向量化按钮
3. 验证embedding表中的page_index_node_id不为空
"""

import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartdoc.settings')
django.setup()

from django.db.models import QuerySet
from knowledge.models import Knowledge, Document, Paragraph, Embedding, PageIndexNode
from common.db.search import native_search


def test_page_index_embedding_fix():
    """测试PageIndex向量化修复"""
    
    print("=" * 80)
    print("测试PageIndex向量化修复")
    print("=" * 80)
    
    # 1. 查找启用了PageIndex的知识库
    try:
        from config.page_index_config import PageIndexConfig
        knowledge_list = QuerySet(Knowledge).all()
        
        test_knowledge = None
        for knowledge in knowledge_list:
            if PageIndexConfig.is_enabled(str(knowledge.id)):
                test_knowledge = knowledge
                break
        
        if not test_knowledge:
            print("❌ 未找到启用PageIndex的知识库")
            print("提示：请先在config/page_index_config.py中启用至少一个知识库")
            return False
        
        print(f"✅ 找到测试知识库: {test_knowledge.name} (ID: {test_knowledge.id})")
        
    except ImportError:
        print("❌ PageIndexConfig未配置")
        return False
    
    # 2. 查找该知识库下的文档
    documents = QuerySet(Document).filter(knowledge=test_knowledge)[:1]
    if not documents:
        print("❌ 知识库中没有文档")
        return False
    
    test_document = documents[0]
    print(f"✅ 找到测试文档: {test_document.name} (ID: {test_document.id})")
    
    # 3. 检查文档的段落
    paragraphs = QuerySet(Paragraph).filter(document=test_document)
    if not paragraphs:
        print("❌ 文档中没有段落")
        return False
    
    print(f"✅ 文档有 {paragraphs.count()} 个段落")
    
    # 4. 检查PageIndexNode是否已构建
    nodes = QuerySet(PageIndexNode).filter(document=test_document)
    print(f"\n📊 PageIndexNode状态:")
    print(f"   - 节点数量: {nodes.count()}")
    
    if nodes.count() > 0:
        for node in nodes[:5]:
            print(f"   - 节点: {node.title} (level={node.level}, id={node.id})")
    
    # 5. 检查Embedding表中的page_index_node_id
    embeddings = QuerySet(Embedding).filter(document=test_document)
    print(f"\n📊 Embedding状态:")
    print(f"   - 向量数量: {embeddings.count()}")
    
    if embeddings.count() > 0:
        with_node_id = embeddings.filter(page_index_node_id__isnull=False).count()
        without_node_id = embeddings.filter(page_index_node_id__isnull=True).count()
        
        print(f"   - 有page_index_node_id: {with_node_id}")
        print(f"   - 无page_index_node_id: {without_node_id}")
        
        # 显示前几个embedding的详情
        print(f"\n📋 前5个Embedding详情:")
        for emb in embeddings[:5]:
            paragraph = QuerySet(Paragraph).filter(id=emb.paragraph_id).first()
            para_title = paragraph.title if paragraph else "N/A"
            node_id = emb.page_index_node_id if emb.page_index_node_id else "NULL"
            print(f"   - Paragraph: {para_title[:30]}... → Node ID: {node_id}")
        
        # 验证结果
        if without_node_id > 0:
            print(f"\n❌ 发现问题: {without_node_id} 个embedding的page_index_node_id为空")
            print("   建议：重新点击向量化按钮，应该会自动修复")
            return False
        else:
            print(f"\n✅ 所有embedding都已正确关联到PageIndexNode")
            return True
    else:
        print("   - 尚未向量化")
        return False


def show_fix_instructions():
    """显示修复说明"""
    print("\n" + "=" * 80)
    print("修复说明")
    print("=" * 80)
    print("""
本次修复的核心改动：

1. 在 apps/knowledge/task/embedding.py 中：
   - 在向量化之前，先调用 _build_page_index_for_document_if_needed()
   - 确保 page_index_node 表有数据后再生成 embedding
   
2. 在 apps/knowledge/serializers/common.py 中：
   - 新增 _build_page_index_for_document_if_needed() 函数
   - 在向量化前检查并构建 PageIndex（如果需要）

修复流程：
   向量化按钮 → 构建PageIndex → 生成Embedding → 同步关联关系
   
现在点击"向量化"按钮时：
   1. 先检查是否需要构建PageIndex
   2. 如果需要且未构建，则先构建PageIndex节点
   3. 然后生成embedding，此时会自动关联到page_index_node_id
   4. 最后再次同步，确保关联关系正确
""")


if __name__ == '__main__':
    success = test_page_index_embedding_fix()
    show_fix_instructions()
    
    if success:
        print("\n✅ 测试通过！PageIndex向量化已正确配置")
    else:
        print("\n⚠️  请按照上述说明检查配置")

