#!/usr/bin/env python
# coding=utf-8
"""
PageIndex树构建工具
用于从现有文档构建PageIndex树
"""
import os
import sys
import django

# 设置路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, 'apps')
sys.path.insert(0, APP_DIR)

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maxkb.settings')
django.setup()

from knowledge.models import Document, Knowledge
from knowledge.page_index import PageIndex


def build_for_knowledge(knowledge_id: str, chunk_size: int = 1000):
    """
    为指定知识库构建PageIndex
    
    Args:
        knowledge_id: 知识库ID
        chunk_size: 分块大小
    """
    print(f"开始为知识库 {knowledge_id} 构建PageIndex...")
    
    # 获取知识库
    try:
        knowledge = Knowledge.objects.get(id=knowledge_id)
    except Knowledge.DoesNotExist:
        print(f"❌ 知识库不存在: {knowledge_id}")
        return False
    
    # 获取所有文档
    documents = Document.objects.filter(
        knowledge=knowledge,
        status='SUCCESS'
    )
    
    print(f"📄 找到 {documents.count()} 个文档")
    
    if documents.count() == 0:
        print("⚠️  没有需要处理的文档")
        return True
    
    # 构建PageIndex
    try:
        page_index = PageIndex.from_documents(
            documents=list(documents),
            knowledge=knowledge,
            chunk_size=chunk_size
        )
        
        # 显示统计信息
        stats = page_index.get_statistics()
        print(f"\n✅ PageIndex构建成功！")
        print(f"   总节点数: {stats['total_nodes']}")
        print(f"   最大深度: {stats['max_depth']}")
        print(f"   深度分布: {stats['depth_distribution']}")
        
        # 显示树摘要
        print(f"\n📊 树结构摘要（前3层）：")
        print(page_index.get_tree_summary(max_depth=3))
        
        return True
        
    except Exception as e:
        print(f"❌ 构建失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def build_all_knowledge():
    """为所有知识库构建PageIndex"""
    knowledges = Knowledge.objects.all()
    print(f"找到 {knowledges.count()} 个知识库\n")
    
    success_count = 0
    for kb in knowledges:
        print(f"{'='*60}")
        print(f"处理知识库: {kb.name} ({kb.id})")
        print(f"{'='*60}")
        
        if build_for_knowledge(str(kb.id)):
            success_count += 1
        print()
    
    print(f"\n{'='*60}")
    print(f"完成: {success_count}/{knowledges.count()} 个知识库构建成功")
    print(f"{'='*60}")


def print_usage():
    """打印使用说明"""
    print("用法:")
    print("  python build_page_index.py <knowledge_id> [chunk_size]")
    print("  python build_page_index.py --all")
    print("\n示例:")
    print("  python build_page_index.py abc-123-def 1000")
    print("  python build_page_index.py --all")
    print("\n参数说明:")
    print("  knowledge_id: 知识库UUID")
    print("  chunk_size:   分块大小（默认1000）")
    print("  --all:        为所有知识库构建")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    if sys.argv[1] == '--all':
        build_all_knowledge()
    else:
        knowledge_id = sys.argv[1]
        chunk_size = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
        build_for_knowledge(knowledge_id, chunk_size)
