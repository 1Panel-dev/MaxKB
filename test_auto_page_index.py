#!/usr/bin/env python
# coding=utf-8
"""
PageIndex自动构建功能测试脚本
验证文档上传后PageIndex是否自动构建
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
from config.page_index_config import PageIndexConfig


def print_separator(char='=', length=60):
    """打印分隔线"""
    print(char * length)


def test_auto_build_config():
    """测试1：检查自动构建配置"""
    print_separator()
    print("测试1: 检查PageIndex自动构建配置")
    print_separator()
    
    print(f"全局开关（ENABLE_PAGE_INDEX）: {PageIndexConfig.ENABLE_PAGE_INDEX}")
    print(f"知识库配置数量: {len(PageIndexConfig.KNOWLEDGE_CONFIG)}")
    
    knowledges = Knowledge.objects.all()
    print(f"\n知识库列表（{knowledges.count()}个）：")
    
    for kb in knowledges[:5]:  # 只显示前5个
        enabled = PageIndexConfig.is_enabled(str(kb.id))
        status = "✅ 启用" if enabled else "❌ 禁用"
        print(f"  {status} - {kb.name} ({kb.id})")
    
    if knowledges.count() > 5:
        print(f"  ... 还有 {knowledges.count() - 5} 个知识库")
    
    print()


def test_auto_build_trigger():
    """测试2：模拟自动构建触发"""
    print_separator()
    print("测试2: 模拟自动构建触发")
    print_separator()
    
    knowledges = Knowledge.objects.all()
    if knowledges.count() == 0:
        print("❌ 没有知识库")
        return False
    
    kb = knowledges[0]
    knowledge_id = str(kb.id)
    
    print(f"使用知识库: {kb.name} ({knowledge_id})")
    
    # 导入自动构建函数
    try:
        from knowledge.serializers.common import _auto_build_page_index
        
        print("\n正在触发自动构建...")
        
        # 调用自动构建
        _auto_build_page_index(knowledge_id=knowledge_id, document_id=None)
        
        print("✅ 自动构建触发成功！")
        
    except ImportError as e:
        print(f"❌ 无法导入自动构建函数: {e}")
        return False
    except Exception as e:
        print(f"❌ 自动构建失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 检查构建结果
    print()
    node_count = PageIndexNode.objects.filter(knowledge_id=knowledge_id).count()
    print(f"PageIndex节点数: {node_count}")
    
    if node_count > 0:
        print("✅ PageIndex已自动构建！")
        return True
    else:
        print("⚠️  PageIndex节点数为0")
        return False


def test_document_auto_build(document_id):
    """测试3：单文档自动构建"""
    print_separator()
    print("测试3: 单文档自动构建")
    print_separator()
    
    try:
        from knowledge.models import Document
        doc = Document.objects.get(id=document_id)
        print(f"文档: {doc.name} ({document_id})")
        print(f"状态: {doc.status}")
        
        # 检查PageIndex
        node_count = PageIndexNode.objects.filter(document_id=document_id).count()
        print(f"PageIndex节点数: {node_count}")
        
        if node_count > 0:
            print("✅ 该文档的PageIndex已构建")
        else:
            print("⚠️  该文档的PageIndex未构建")
            print("   提示：需要文档状态为SUCCESS才会触发自动构建")
        
        return True
        
    except Document.DoesNotExist:
        print(f"❌ 文档不存在: {document_id}")
        return False


def print_next_steps():
    """打印下一步操作建议"""
    print_separator()
    print("下一步操作建议")
    print_separator()
    
    print("\n1. 启用PageIndex自动构建")
    print("   修改 config/page_index_config.py:")
    print("   class PageIndexConfig:")
    print("       ENABLE_PAGE_INDEX = True")
    
    print("\n2. 上传测试文档")
    print("   通过MaxKB Web界面上传文档")
    print("   等待文档处理完成（状态变为SUCCESS）")
    print("   PageIndex会自动构建")
    
    print("\n3. 验证自动构建")
    print(f"   检查数据库: SELECT COUNT(*) FROM page_index_node")
    print(f"   查看日志: grep 'PageIndex built' maxkb.log")
    print(f"   运行测试: python {sys.argv[0]} --test 2")
    
    print("\n4. 查看PageIndex使用指南")
    print("   文档: PageIndex使用指南.md")
    print("   文档: PageIndex自动构建说明.md")
    
    print()


def main():
    """主函数"""
    print_separator()
    print("PageIndex自动构建功能测试")
    print_separator()
    print()
    
    # 测试1: 配置检查
    test_auto_build_config()
    
    # 测试2: 自动构建触发
    test_auto_build_trigger()
    
    # 如果有document_id参数，测试单文档
    if len(sys.argv) > 2 and sys.argv[1] == '--test' and sys.argv[2] == '3':
        if len(sys.argv) > 3:
            document_id = sys.argv[3]
            test_document_auto_build(document_id)
    
    # 下一步建议
    print_next_steps()
    
    print_separator()
    print("测试完成！")
    print_separator()


if __name__ == '__main__':
    # 显示使用说明
    if len(sys.argv) == 1:
        print("用法:")
        print("  python test_auto_page_index.py                    # 运行所有测试")
        print("  python test_auto_page_index.py --test 2        # 测试自动构建触发")
        print("  python test_auto_page_index.py --test 3 <doc_id>  # 测试单文档构建")
        print("\n示例:")
        print("  python test_auto_page_index.py --test 2")
        print("  python test_auto_page_index.py --test 3 abc-123-def")
        sys.exit(0)
    
    main()
