#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
诊断配置文件加载情况
"""
import os
import sys

# 添加项目路径
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

print("=" * 80)
print("MaxKB 配置诊断工具")
print("=" * 80)

# 检查环境变量
print("\n1. 环境变量检查:")
print(f"   MAXKB_CONFIG: {os.getenv('MAXKB_CONFIG', '未设置')}")
print(f"   MAXKB_CONFIG_TYPE: {os.getenv('MAXKB_CONFIG_TYPE', '未设置')}")
print(f"   SERVER_NAME: {os.getenv('SERVER_NAME', '未设置')}")

# 检查配置文件路径
print("\n2. 配置文件检查:")
config_paths = [
    os.path.join(project_dir, 'config.yaml'),
    os.path.join(project_dir, 'config.yml'),
    os.path.join(project_dir, 'config_example.yml'),
    '/opt/maxkb/conf/config.yaml',
    '/opt/maxkb/conf/config.yml'
]

for path in config_paths:
    exists = "✓ 存在" if os.path.isfile(path) else "✗ 不存在"
    print(f"   {path}: {exists}")

# 加载配置并显示
print("\n3. 实际加载的配置:")
try:
    from apps.maxkb.const import CONFIG
    
    print(f"   DB_HOST: {CONFIG.get('DB_HOST')}")
    print(f"   DB_PORT: {CONFIG.get('DB_PORT')}")
    print(f"   DB_NAME: {CONFIG.get('DB_NAME')}")
    print(f"   DB_USER: {CONFIG.get('DB_USER')}")
    print(f"   DB_PASSWORD: {CONFIG.get('DB_PASSWORD')}")
    print(f"   DB_ENGINE: {CONFIG.get('DB_ENGINE')}")
    print(f"   REDIS_HOST: {CONFIG.get('REDIS_HOST')}")
    print(f"   REDIS_PORT: {CONFIG.get('REDIS_PORT')}")
    print(f"   DEBUG: {CONFIG.get('DEBUG')}")
    
    # 显示完整的数据库配置
    print("\n4. Django 数据库配置:")
    db_setting = CONFIG.get_db_setting()
    for key, value in db_setting.items():
        if key != 'PASSWORD':  # 不显示密码
            print(f"   {key}: {value}")
        else:
            print(f"   {key}: ***隐藏***")
    
except Exception as e:
    print(f"   错误：{e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
