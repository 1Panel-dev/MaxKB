#!/usr/bin/env python
# coding=utf-8
"""
PageIndex集成测试脚本
验证PageIndex与MaxKB检索流程的集成
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

from knowledge.models import Knowledge, Document, PageIndexNode
from knowledge.page_index.page_index_retriever import PageIndexRetriever
from config.page_index_config import PageIndexConfig


def print_separator(char='=', length=60):
    """打印分隔线"""
    print(char * length)


def test_integration():
    """测试PageIndex集成"""
    print_separator()
    print("PageIndex集成测试")
    print_separator()
    print()
    
    # 1. 检查配置
    print("测试1: 检查PageIndex配置")
    print_separator()
    
    knowledges = Knowledge.objects.all()
    if knowledges.count() == 0:
        print("❌ 没有知识库")
        return False
    
    kb = knowledges[0]
    knowledge_id = str(kb.id)
    
    print(f"知识库: {kb.name} ({knowledge_id})")
    print(f"PageIndex启用: {PageIndexConfig.is_enabled(knowledge_id)}")
    print(f"默认配置: {PageIndexConfig.DEFAULT_CONFIG}")
    print()
    
    # 2. 检查PageIndex是否已构建
    print("测试2: 检查PageIndex构建状态")
    print_separator()
    
    node_count = PageIndexNode.objects.filter(knowledge_id=knowledge_id).count()
    
    if node_count == 0:
        print("❌ PageIndex未构建，请先运行：")
        print(f"   python build_page_index.py {knowledge_id}")
        return False
    
    print(f"✅ PageIndex已构建，共 {node_count} 个节点")
    print()
    
    # 3. 测试检索器创建
    print("测试3: 创建PageIndexRetriever")
    print_separator()
    
    try:
        config = PageIndexConfig.get_config(knowledge_id)
        retriever = PageIndexRetriever(
            knowledge_id=knowledge_id,
            **config
        )
        
        print("✅ PageIndexRetriever创建成功")
        print(f"   配置: {config}")
        print()
        
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 4. 测试树信息查询
    print("测试4: 查询树结构信息")
    print_separator()
    
    root_nodes = PageIndexNode.objects.filter(
        knowledge_id=knowledge_id,
        level=0
    )
    
    if root_nodes.exists():
        root = root_nodes[0]
        print(f"根节点: {root.title}")
        
        path_info = retriever.get_tree_path(str(root.id))
        if path_info:
            print(f"   完整路径: {path_info.get('full_path')}")
            print(f"   字符数: {path_info.get('char_count')}")
        
        # 获取子节点
        children = PageIndexNode.objects.filter(parent=root)
        print(f"   子节点数: {children.count()}")
        for child in children[:3]:  # 只显示前3个
            print(f"     - {child.title}")
        
        if children.count() > 3:
            print(f"     ... 还有 {children.count() - 3} 个节点")
        
        print()
    
    # 5. 性能对比建议
    print("测试5: 性能优化建议")
    print_separator()
    
    stats = {
        'total_nodes': node_count,
        'avg_nodes_per_level': node_count // max(1, PageIndexNode.objects.filter(
            knowledge_id=knowledge_id
        ).values_list('level', flat=True).distinct().count())
    }
    
    print(f"📊 统计信息:")
    print(f"   总节点数: {stats['total_nodes']}")
    print(f"   平均每层节点数: {stats['avg_nodes_per_level']}")
    print()
    
    print(f"💡 优化建议:")
    if stats['total_nodes'] < 10:
        print("   - 节点数较少，可以考虑增加chunk_size")
    elif stats['total_nodes'] > 100:
        print("   - 节点数较多，建议增加similarity_threshold")
    
    if stats['avg_nodes_per_level'] > 20:
        print("   - 每层节点数较多，建议使用tree_filter减少候选集")
    
    print()
    print_separator()
    print("✅ 集成测试完成！")
    print_separator()
    
    return True


if __name__ == '__main__':
    test_integration()
