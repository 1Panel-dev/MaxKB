#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
诊断PageIndex向量化问题
检查为什么重新上传文档后page_index_node_id仍然为空
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


def diagnose_document(document_id: str):
    """诊断指定文档的PageIndex状态"""
    
    print("=" * 80)
    print(f"诊断文档: {document_id}")
    print("=" * 80)
    
    # 1. 检查文档是否存在
    document = QuerySet(Document).filter(id=document_id).first()
    if not document:
        print(f"❌ 文档不存在: {document_id}")
        return
    
    print(f"✅ 文档: {document.name}")
    print(f"   知识库ID: {document.knowledge_id}")
    
    # 2. 检查知识库是否启用PageIndex
    try:
        from config.page_index_config import PageIndexConfig
        is_enabled = PageIndexConfig.is_enabled(str(document.knowledge_id))
        print(f"   PageIndex启用: {'是' if is_enabled else '否'}")
        
        if not is_enabled:
            print("\n⚠️  该知识库未启用PageIndex，请先在config/page_index_config.py中启用")
            return
    except ImportError:
        print("   PageIndex配置: 未找到")
        return
    
    # 3. 检查段落数量
    paragraphs = QuerySet(Paragraph).filter(document=document)
    print(f"\n📊 段落统计:")
    print(f"   总数: {paragraphs.count()}")
    
    if paragraphs.count() == 0:
        print("   ❌ 文档没有段落")
        return
    
    # 显示前3个段落
    for i, para in enumerate(paragraphs[:3]):
        print(f"   [{i+1}] {para.title[:50] if para.title else '(无标题)'}...")
    
    # 4. 检查PageIndexNode
    nodes = QuerySet(PageIndexNode).filter(document=document)
    print(f"\n📊 PageIndexNode统计:")
    print(f"   节点数: {nodes.count()}")
    
    if nodes.count() == 0:
        print("   ❌ 没有PageIndex节点！")
        print("\n🔍 可能的原因:")
        print("   1. 段落创建后没有触发PageIndex构建")
        print("   2. PageIndex构建过程中出错")
        print("   3. 文档内容无法解析出标题结构")
        print("\n💡 建议:")
        print("   1. 检查日志中是否有 '[PageIndex] Auto building' 相关信息")
        print("   2. 手动触发构建: python build_page_index.py <knowledge_id>")
    else:
        # 显示节点结构
        print(f"\n📋 节点结构:")
        for node in nodes[:10]:
            indent = "  " * node.level
            print(f"   {indent}[L{node.level}] {node.title} (id={str(node.id)[:8]}...)")
    
    # 5. 检查Embedding
    embeddings = QuerySet(Embedding).filter(document=document)
    print(f"\n📊 Embedding统计:")
    print(f"   总数: {embeddings.count()}")
    
    if embeddings.count() == 0:
        print("   ⚠️  尚未向量化")
        print("\n💡 建议: 点击'向量化'按钮进行向量化")
    else:
        with_node = embeddings.filter(page_index_node_id__isnull=False).count()
        without_node = embeddings.filter(page_index_node_id__isnull=True).count()
        
        print(f"   有page_index_node_id: {with_node}")
        print(f"   无page_index_node_id: {without_node}")
        
        if without_node > 0:
            print(f"\n   ❌ 发现 {without_node} 个embedding的page_index_node_id为空！")
            
            # 分析原因
            print(f"\n🔍 分析原因:")
            
            # 检查是否是向量化时机问题
            if nodes.count() == 0:
                print("   原因: 向量化时PageIndexNode表为空")
                print("   解决: 先构建PageIndex，再重新向量化")
            else:
                print("   原因: 向量化时PageIndexNode已存在，但关联失败")
                print("   可能是段落标题与节点标题不匹配")
                
                # 显示示例
                print(f"\n   示例对比:")
                for emb in embeddings.filter(page_index_node_id__isnull=True)[:3]:
                    para = QuerySet(Paragraph).filter(id=emb.paragraph_id).first()
                    if para:
                        print(f"   - 段落标题: '{para.title}'")
                        matching_node = nodes.filter(title=para.title).first()
                        if matching_node:
                            print(f"     → 找到匹配节点: {matching_node.id}")
                        else:
                            print(f"     → 未找到匹配节点")
        else:
            print(f"\n   ✅ 所有embedding都已正确关联到PageIndexNode")
    
    # 6. 给出修复建议
    print(f"\n" + "=" * 80)
    print("修复建议")
    print("=" * 80)
    
    if nodes.count() == 0:
        print("""
1. PageIndex节点未构建，需要先构建:
   方法1: 重新上传文档（会自动触发构建）
   方法2: 手动构建: python build_page_index.py <knowledge_id>
   
2. 构建完成后，再点击"向量化"按钮
""")
    elif embeddings.count() == 0:
        print("""
1. PageIndex节点已构建，但尚未向量化
2. 点击"向量化"按钮即可
""")
    elif without_node > 0:
        print("""
1. PageIndex节点已构建，但embedding关联失败
2. 可能原因:
   - 向量化时PageIndex尚未构建（时序问题）
   - 段落标题与节点标题不匹配
   
3. 解决方法:
   方法1: 重新点击"向量化"按钮（现在应该会自动先构建PageIndex）
   方法2: 运行同步脚本:
          python -c "
          from knowledge.models import Document
          from knowledge.serializers.common import _sync_page_index_embeddings_for_document
          doc = Document.objects.get(id='<document_id>')
          _sync_page_index_embeddings_for_document(doc)
          "
""")
    else:
        print("""
✅ 一切正常！PageIndex已正确配置并关联。
""")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python diagnose_page_index_issue.py <document_id>")
        print("\n提示: 可以从数据库或UI中获取document_id")
        sys.exit(1)
    
    document_id = sys.argv[1]
    diagnose_document(document_id)

