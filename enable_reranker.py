#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速启用Reranker脚本
使用方法: python enable_reranker.py <application_id> <reranker_model_id>
"""
import sys
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maxkb.settings')
django.setup()

from application.models import Application

def enable_reranker(app_id, reranker_model_id, top_n=3):
    """
    为指定应用启用Reranker
    
    Args:
        app_id: 应用ID
        reranker_model_id: Reranker模型ID
        top_n: 重排序后返回的结果数量
    """
    try:
        app = Application.objects.get(id=app_id)
        
        # 更新knowledge_setting
        if not app.knowledge_setting:
            app.knowledge_setting = {}
        
        app.knowledge_setting['enable_reranker'] = True
        app.knowledge_setting['reranker_model_id'] = reranker_model_id
        app.knowledge_setting['reranker_top_n'] = top_n
        
        app.save()
        
        print(f"✅ 成功为应用 '{app.name}' (ID: {app_id}) 启用Reranker")
        print(f"   - Reranker模型ID: {reranker_model_id}")
        print(f"   - Top N: {top_n}")
        
        return True
    except Application.DoesNotExist:
        print(f"❌ 错误: 找不到ID为 {app_id} 的应用")
        return False
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False

def list_applications():
    """列出所有应用"""
    apps = Application.objects.all()
    print("\n📋 所有应用列表:")
    print("-" * 80)
    for app in apps:
        reranker_status = "✓" if app.knowledge_setting.get('enable_reranker') else "✗"
        print(f"[{reranker_status}] {app.name}")
        print(f"    ID: {app.id}")
        print(f"    描述: {app.desc or '无'}")
        print("-" * 80)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  1. 列出所有应用: python enable_reranker.py list")
        print("  2. 启用Reranker: python enable_reranker.py <app_id> <reranker_model_id> [top_n]")
        print("\n示例:")
        print("  python enable_reranker.py list")
        print("  python enable_reranker.py abc-123 def-456 3")
        sys.exit(1)
    
    if sys.argv[1] == "list":
        list_applications()
    else:
        app_id = sys.argv[1]
        if len(sys.argv) < 3:
            print("❌ 错误: 请提供Reranker模型ID")
            sys.exit(1)
        
        reranker_model_id = sys.argv[2]
        top_n = int(sys.argv[3]) if len(sys.argv) > 3 else 3
        
        enable_reranker(app_id, reranker_model_id, top_n)

