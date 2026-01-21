#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复文档向量化卡在排队中的问题
使用方法: python fix_vectorization_queue.py
"""
import sys
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maxkb.settings')
django.setup()

from knowledge.models import Document, Paragraph, TaskType, State
from knowledge.task.embedding import embedding_by_document
from django.db.models import QuerySet
import subprocess

def check_celery_status():
    """检查Celery Worker状态"""
    print("\n🔍 检查Celery Worker状态...")
    try:
        result = subprocess.run(
            ['celery', '-A', 'ops', 'inspect', 'active'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout:
            print("✅ Celery Worker 正在运行")
            print(result.stdout)
            return True
        else:
            print("❌ Celery Worker 未运行或无响应")
            return False
    except Exception as e:
        print(f"❌ 无法检查Celery状态: {str(e)}")
        return False

def check_redis_connection():
    """检查Redis连接"""
    print("\n🔍 检查Redis连接...")
    try:
        from django.core.cache import cache
        cache.set('test_key', 'test_value', 10)
        value = cache.get('test_key')
        if value == 'test_value':
            print("✅ Redis连接正常")
            return True
        else:
            print("❌ Redis连接异常")
            return False
    except Exception as e:
        print(f"❌ Redis连接失败: {str(e)}")
        return False

def list_queued_documents():
    """列出所有排队中的文档"""
    print("\n📋 查找排队中的文档...")
    
    # 查找状态为PENDING的文档
    pending_docs = Document.objects.filter(status__contains='0')  # State.PENDING = 0
    
    if not pending_docs.exists():
        print("✅ 没有排队中的文档")
        return []
    
    print(f"找到 {pending_docs.count()} 个排队中的文档:")
    print("-" * 80)
    
    doc_list = []
    for doc in pending_docs:
        print(f"文档: {doc.name}")
        print(f"  ID: {doc.id}")
        print(f"  知识库ID: {doc.knowledge_id}")
        print(f"  状态: {doc.status}")
        print(f"  创建时间: {doc.create_time}")
        print("-" * 80)
        doc_list.append(doc)
    
    return doc_list

def retry_failed_tasks(doc_list):
    """重新提交失败的任务"""
    if not doc_list:
        return
    
    print(f"\n🔄 准备重新提交 {len(doc_list)} 个文档的向量化任务...")
    
    for doc in doc_list:
        try:
            # 获取embedding模型ID
            from knowledge.models import Knowledge
            knowledge = Knowledge.objects.get(id=doc.knowledge_id)
            model_id = knowledge.embedding_model_id
            
            print(f"重新提交: {doc.name}")
            embedding_by_document.delay(str(doc.id), str(model_id))
            print(f"  ✅ 已提交到队列")
        except Exception as e:
            print(f"  ❌ 提交失败: {str(e)}")

def show_celery_start_command():
    """显示启动Celery的命令"""
    print("\n" + "="*80)
    print("📌 如何启动Celery Worker:")
    print("="*80)
    print("\n方法1: 使用Django管理命令（推荐）")
    print("  python manage.py celery celery")
    print("\n方法2: 直接使用Celery命令")
    print("  celery -A ops worker -P threads -l info -c 10 -Q celery --heartbeat-interval 10")
    print("\n方法3: 使用MaxKB服务管理")
    print("  python manage.py start all")
    print("\n" + "="*80)

def main():
    print("="*80)
    print("MaxKB 文档向量化问题诊断工具")
    print("="*80)
    
    # 1. 检查Redis
    redis_ok = check_redis_connection()
    
    # 2. 检查Celery
    celery_ok = check_celery_status()
    
    # 3. 列出排队文档
    doc_list = list_queued_documents()
    
    # 4. 诊断结果
    print("\n" + "="*80)
    print("📊 诊断结果:")
    print("="*80)
    
    if not redis_ok:
        print("❌ Redis未连接 - 请检查Redis服务是否启动")
        print("   启动Redis: redis-server")
        return
    
    if not celery_ok:
        print("❌ Celery Worker未运行 - 这是文档卡在排队中的主要原因！")
        show_celery_start_command()
        
        if doc_list:
            print("\n💡 建议操作:")
            print("1. 先启动Celery Worker（使用上面的命令）")
            print("2. 等待几秒后，文档应该会自动开始处理")
            print("3. 如果还是不行，再次运行此脚本选择重新提交任务")
    else:
        print("✅ Celery Worker正在运行")
        
        if doc_list:
            print(f"\n⚠️  发现 {len(doc_list)} 个排队中的文档")
            print("\n可能的原因:")
            print("1. Celery Worker刚刚启动，任务正在处理中")
            print("2. 任务队列积压")
            print("3. 向量模型配置有问题")
            
            choice = input("\n是否重新提交这些任务? (y/n): ")
            if choice.lower() == 'y':
                retry_failed_tasks(doc_list)
                print("\n✅ 任务已重新提交，请等待处理...")
        else:
            print("✅ 所有文档都已处理完成")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()

