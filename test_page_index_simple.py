#!/usr/bin/env python
# coding=utf-8
"""
PageIndex功能测试脚本
快速验证PageIndex的核心功能
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

from knowledge.models import Knowledge, Document, PageIndexNode, Embedding
from knowledge.page_index.page_index_retriever import PageIndexRetriever


def print_separator(char='=', length=60):
    """打印分隔线"""
    print(char * length)


def test_1_check_database():
    """测试1：检查数据库表是否创建成功"""
    print_separator()
    print("测试1: 检查数据库表")
    print_separator()
    
    try:
        # 检查PageIndexNode表
        node_count = PageIndexNode.objects.count()
        print(f"✅ PageIndexNode表存在，当前有 {node_count} 个节点")
        
        # 检查Embedding表是否有PageIndex相关字段
        embeddings = Embedding.objects.all()[:1]
        if embeddings.exists():
            emb = embeddings[0]
            has_tree_fields = hasattr(emb, 'page_index_node')
            print(f"✅ Embedding表有PageIndex关联: {has_tree_fields}")
        else:
            print("⚠️  Embedding表暂时没有数据")
        
        return True
    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")
        return False


def test_2_list_knowledges():
    """测试2：列出所有知识库"""
    print_separator()
    print("测试2: 列出可用知识库")
    print_separator()
    
    knowledges = Knowledge.objects.all()
    
    if knowledges.count() == 0:
        print("❌ 没有找到任何知识库")
        return False
    
    print(f"找到 {knowledges.count()} 个知识库:\n")
    
    for i, kb in enumerate(knowledges, 1):
        doc_count = Document.objects.filter(knowledge=kb).count()
        print(f"{i}. {kb.name}")
        print(f"   ID: {kb.id}")
        print(f"   文档数: {doc_count}")
        print()
    
    return True


def test_3_build_page_index(knowledge_id=None):
    """测试3：构建PageIndex"""
    print_separator()
    print("测试3: 构建PageIndex")
    print_separator()
    
    # 如果没有指定知识库，使用第一个
    if not knowledge_id:
        kb = Knowledge.objects.first()
        if not kb:
            print("❌ 没有可用的知识库")
            return False
        knowledge_id = str(kb.id)
    
    print(f"使用知识库: {knowledge_id}")
    
    try:
        from knowledge.page_index import PageIndex
        
        knowledge = Knowledge.objects.get(id=knowledge_id)
        documents = Document.objects.filter(knowledge=knowledge)
        
        if documents.count() == 0:
            print("❌ 该知识库没有文档")
            return False
        
        print(f"找到 {documents.count()} 个文档，开始构建...\n")
        
        # 构建PageIndex
        page_index = PageIndex.from_documents(
            documents=list(documents),
            knowledge=knowledge,
            chunk_size=1000
        )
        
        # 显示统计
        stats = page_index.get_statistics()
        print(f"✅ 构建成功！")
        print(f"\n📊 统计信息:")
        print(f"   总节点数: {stats['total_nodes']}")
        print(f"   最大深度: {stats['max_depth']}")
        print(f"   深度分布: {stats['depth_distribution']}")
        
        # 显示树摘要
        print(f"\n🌳 树结构摘要:")
        print(page_index.get_tree_summary(max_depth=2))
        
        return True
        
    except Exception as e:
        print(f"❌ 构建失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_4_retrieval(knowledge_id=None):
    """测试4：检索功能"""
    print_separator()
    print("测试4: 检索功能")
    print_separator()
    
    if not knowledge_id:
        kb = Knowledge.objects.first()
        if not kb:
            print("❌ 没有可用的知识库")
            return False
        knowledge_id = str(kb.id)
    
    # 检查是否有PageIndex节点
    node_count = PageIndexNode.objects.filter(knowledge_id=knowledge_id).count()
    if node_count == 0:
        print("❌ 该知识库没有PageIndex节点，请先运行测试3构建")
        return False
    
    print(f"知识库有 {node_count} 个PageIndex节点")
    
    try:
        retriever = PageIndexRetriever(
            knowledge_id=knowledge_id,
            use_tree_filter=True,
            search_mode='blend',
            top_n=5
        )
        
        # 模拟查询（需要embedding模型）
        test_query = "如何使用系统？"
        print(f"\n测试查询: {test_query}")
        
        print("\n注意: 完整的检索测试需要embedding模型")
        print("当前仅验证retriever对象创建成功")
        
        # 显示检索器配置
        print(f"\n📝 检索器配置:")
        print(f"   知识库: {knowledge_id}")
        print(f"   启用树过滤: {retriever.use_tree_filter}")
        print(f"   搜索模式: {retriever.search_mode}")
        print(f"   返回数量: {retriever.top_n}")
        
        return True
        
    except Exception as e:
        print(f"❌ 检索器创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """运行所有测试"""
    print_separator()
    print("PageIndex功能测试开始")
    print_separator()
    print()
    
    results = {}
    
    # 测试1: 数据库检查
    results['数据库检查'] = test_1_check_database()
    print()
    
    # 测试2: 列出知识库
    results['列出知识库'] = test_2_list_knowledges()
    print()
    
    # 测试3: 构建PageIndex
    results['构建PageIndex'] = test_3_build_page_index()
    print()
    
    # 测试4: 检索功能
    results['检索功能'] = test_4_retrieval()
    print()
    
    # 汇总结果
    print_separator()
    print("测试结果汇总")
    print_separator()
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    success_count = sum(results.values())
    total_count = len(results)
    
    print(f"\n总计: {success_count}/{total_count} 测试通过")
    print_separator()
    
    return success_count == total_count


def print_usage():
    """打印使用说明"""
    print("用法:")
    print("  python test_page_index_simple.py                    # 运行所有测试")
    print("  python test_page_index_simple.py --test <test_num>   # 运行指定测试")
    print("\n测试编号:")
    print("  1: 数据库检查")
    print("  2: 列出知识库")
    print("  3: 构建PageIndex")
    print("  4: 检索功能")
    print("\n示例:")
    print("  python test_page_index_simple.py --test 1")
    print("  python test_page_index_simple.py --test 3")


if __name__ == '__main__':
    if len(sys.argv) == 1:
        # 运行所有测试
        run_all_tests()
    elif len(sys.argv) == 3 and sys.argv[1] == '--test':
        # 运行指定测试
        test_num = int(sys.argv[2])
        tests = {
            1: test_1_check_database,
            2: test_2_list_knowledges,
            3: test_3_build_page_index,
            4: test_4_retrieval
        }
        
        if test_num in tests:
            tests[test_num]()
        else:
            print(f"❌ 无效的测试编号: {test_num}")
            print_usage()
    else:
        print_usage()
