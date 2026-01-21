#!/usr/bin/env python
# coding=utf-8
"""
PageIndex树构建测试脚本
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

from knowledge.models import Document, Knowledge, PageIndexNode
from knowledge.page_index import PageIndex


def test_tree_structure():
    """测试树结构构建"""
    print("测试1: 树结构构建")
    print("-" * 60)
    
    # 查找有文档的知识库
    kb = Knowledge.objects.filter(
        document__isnull=False
    ).first()
    
    if not kb:
        print("❌ 没有找到包含文档的知识库")
        return False
    
    print(f"📚 知识库: {kb.name}")
    
    # 获取文档
    doc = Document.objects.filter(
        knowledge=kb,
        status='SUCCESS'
    ).first()
    
    if not doc:
        print("❌ 没有找到成功的文档")
        return False
    
    print(f"📄 文档: {doc.name}")
    
    # 构建PageIndex
    try:
        page_index = PageIndex.from_documents(
            documents=[doc],
            knowledge=kb,
            chunk_size=500  # 小分块便于测试
        )
    except Exception as e:
        print(f"❌ 构建PageIndex失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 验证节点数量
    node_count = PageIndexNode.objects.filter(
        knowledge=kb
    ).count()
    
    print(f"✅ 创建节点数: {node_count}")
    
    if node_count == 0:
        print("❌ 没有创建任何节点")
        return False
    
    # 验证树结构
    root_nodes = PageIndexNode.objects.filter(
        knowledge=kb,
        level=0
    )
    
    print(f"✅ 根节点数: {root_nodes.count()}")
    
    for root in root_nodes:
        print(f"   - {root.title} (children: {root.children.count()})")
    
    # 显示统计
    stats = page_index.get_statistics()
    print(f"\n📊 统计信息:")
    print(f"   总节点: {stats['total_nodes']}")
    print(f"   最大深度: {stats['max_depth']}")
    print(f"   深度分布: {stats['depth_distribution']}")
    
    # 显示树摘要
    print(f"\n📋 树摘要:")
    print(page_index.get_tree_summary(max_depth=3))
    
    return True


def test_path_consistency():
    """测试路径一致性"""
    print("\n测试2: 路径一致性")
    print("-" * 60)
    
    kb = Knowledge.objects.filter(
        page_nodes__isnull=False
    ).first()
    
    if not kb:
        print("❌ 没有找到PageIndex数据")
        return False
    
    nodes = PageIndexNode.objects.filter(
        knowledge=kb
    )
    
    print(f"📊 检查 {nodes.count()} 个节点的路径一致性...")
    
    errors = 0
    for node in nodes:
        # 检查路径长度是否与level一致
        if len(node.path) != node.level + 1:
            print(f"❌ 节点 {node.id} 路径不匹配: level={node.level}, path_len={len(node.path)}")
            errors += 1
        
        # 检查父节点
        if node.parent:
            if node.level != node.parent.level + 1:
                print(f"❌ 节点 {node.id} 父子关系错误: node_level={node.level}, parent_level={node.parent.level}")
                errors += 1
    
    if errors == 0:
        print(f"✅ 所有节点路径一致")
        return True
    else:
        print(f"❌ 发现 {errors} 个错误")
        return False


def test_tree_methods():
    """测试树方法"""
    print("\n测试3: 树方法")
    print("-" * 60)
    
    kb = Knowledge.objects.filter(
        page_nodes__isnull=False
    ).first()
    
    if not kb:
        print("❌ 没有找到PageIndex数据")
        return False
    
    page_index = PageIndex(kb)
    
    # 测试get_tree_summary
    try:
        summary = page_index.get_tree_summary(max_depth=2)
        print(f"✅ get_tree_summary: OK")
        print(f"   预览: {summary[:200]}...")
    except Exception as e:
        print(f"❌ get_tree_summary: {e}")
        return False
    
    # 测试get_statistics
    try:
        stats = page_index.get_statistics()
        print(f"✅ get_statistics: OK")
        print(f"   总节点: {stats['total_nodes']}")
        print(f"   最大深度: {stats['max_depth']}")
    except Exception as e:
        print(f"❌ get_statistics: {e}")
        return False
    
    return True


def run_all_tests():
    """运行所有测试"""
    print("="*60)
    print("PageIndex树构建测试")
    print("="*60)
    print()
    
    tests = [
        ("树结构构建", test_tree_structure),
        ("路径一致性", test_path_consistency),
        ("树方法", test_tree_methods),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"❌ 测试失败: {name}")
            import traceback
            traceback.print_exc()
            results[name] = False
        print()
    
    # 总结
    print("="*60)
    print("测试总结")
    print("="*60)
    for name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}: {name}")
    
    all_passed = all(results.values())
    print(f"\n{'='*60}")
    if all_passed:
        print("✅ 所有测试通过！")
    else:
        print("❌ 部分测试失败，请检查错误信息")
    print(f"{'='*60}")
    
    return all_passed


if __name__ == '__main__':
    run_all_tests()
