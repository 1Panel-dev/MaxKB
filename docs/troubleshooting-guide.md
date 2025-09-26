# MaxKB 问题排查与处理文档

## 概述

本文档记录了MaxKB本地开发环境配置过程中遇到的问题及解决方案，供后续开发参考。

## 1. 配置文件路径问题

### 问题现象
```bash
ImportError: Error: No config file found.
You can run `cp config_example.yml /opt/maxkb/conf/config.yml`, and edit it.
```

### 问题分析
MaxKB的配置文件加载逻辑：
- 如果设置了 `MAXKB_CONFIG` 环境变量，从项目根目录读取
- 否则从 `/opt/maxkb/conf` 目录读取（生产环境模式）

### 解决方案
**方案1：设置环境变量（推荐开发环境）**
```bash
export MAXKB_CONFIG=1
# 配置文件放在项目根目录的 config.yml
```

**方案2：创建系统配置目录**
```bash
sudo mkdir -p /opt/maxkb/conf
sudo cp config.yml /opt/maxkb/conf/
sudo chown $USER:$USER /opt/maxkb/conf/config.yml
```

### 预防措施
在 `~/.bashrc` 中添加：
```bash
echo 'export MAXKB_CONFIG=1' >> ~/.bashrc
```

## 2. 系统权限问题

### 问题现象
```bash
PermissionError: [Errno 13] Permission denied: '/opt/maxkb'
```

### 问题分析
MaxKB需要在 `/opt/maxkb` 目录下创建日志和临时文件，但普通用户没有权限。

### 解决方案
```bash
# 创建目录结构
sudo mkdir -p /opt/maxkb/{logs,local,conf}

# 修改目录所有者
sudo chown -R $USER:$USER /opt/maxkb

# 验证权限
ls -la /opt/maxkb
```

### 替代方案
如果不想修改系统目录，可以创建软链接：
```bash
mkdir -p /tmp/maxkb/{logs,local,conf}
sudo ln -sf /tmp/maxkb /opt/maxkb
```

## 3. Python依赖包问题

### 问题现象1：externally-managed-environment
```bash
error: externally-managed-environment
× This environment is externally managed
```

### 解决方案
现代Ubuntu保护系统Python，需要使用虚拟环境：
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 问题现象2：模块缺失
```bash
ModuleNotFoundError: No module named 'pydub'
```

### 解决方案
**一次性安装所有依赖：**
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**分批安装策略：**
```bash
# 1. Django核心
pip install django==5.2.6 drf-spectacular[sidecar]==0.28.0 psycopg[binary]==3.2.9

# 2. 基础依赖
pip install python-dotenv==1.1.1 pytz==2025.2 beautifulsoup4==4.13.4

# 3. 音频处理
pip install pydub==0.25.1 pysilk==0.0.1

# 4. 任务队列
pip install celery[sqlalchemy]==5.5.3 django-celery-beat==2.8.1
```

### 依赖冲突处理
```bash
# 检查依赖冲突
pip check

# 强制重装冲突包
pip install --upgrade --force-reinstall [package_name]
```

## 4. 数据库连接问题

### 问题现象：数据库引擎配置错误
```bash
# 错误的配置
DB_ENGINE: django.db.backends.postgresql_psycopg2

# 正确的配置
DB_ENGINE: dj_db_conn_pool.backends.postgresql
```

### 问题分析
MaxKB使用了数据库连接池，需要使用专门的后端引擎。

### 解决方案
修改 `config.yml` 文件：
```yaml
DB_ENGINE: dj_db_conn_pool.backends.postgresql  # 使用连接池版本
```

### 数据库连接测试
```bash
# 测试数据库连接
python -c "
import sys, os, django
sys.path.insert(0, 'apps')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maxkb.settings')
os.environ['MAXKB_CONFIG'] = '1'
django.setup()
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('SELECT 1')
    print('数据库连接成功!')
"
```

## 5. Django迁移冲突

### 问题现象
```bash
CommandError: Conflicting migrations detected; multiple leaf nodes in the migration graph:
(0003_add_display_fields_to_version, 0003_application_stt_model_params_setting_and_more in application).
To fix them run 'python manage.py makemigrations --merge'
```

### 问题分析
同一个应用有两个编号相同的并行迁移，Django不知道执行顺序。

### 解决方案
```bash
# 1. 合并迁移冲突
python apps/manage.py makemigrations --merge

# 2. 选择合并策略（通常选择默认）
# Django会提示选择，按回车选择默认即可

# 3. 执行合并后的迁移
python apps/manage.py migrate

# 4. 验证迁移状态
python apps/manage.py showmigrations
```

### 预防措施
定期同步代码时检查迁移状态：
```bash
python apps/manage.py showmigrations | grep "\[ \]"
```

## 6. 启动方式选择

### 问题现象
`main.py` 启动失败，但直接用Django可以启动。

### 问题分析
`main.py` 会自动执行迁移和静态文件收集，如果这些步骤失败会阻止启动。

### 解决方案
**方案1：直接使用Django启动（推荐）**
```bash
export MAXKB_CONFIG=1
python apps/manage.py runserver 0.0.0.0:8080
```

**方案2：解决迁移问题后使用main.py**
```bash
# 先解决迁移冲突
python apps/manage.py makemigrations --merge
python apps/manage.py migrate

# 再使用main.py启动
python main.py dev web
```

**方案3：创建自定义启动脚本**
```python
# start_dev.py
import os, sys, django
from django.core import management

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, 'apps')
os.chdir(BASE_DIR)
sys.path.insert(0, APP_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "maxkb.settings")
django.setup()

management.call_command('runserver', "0.0.0.0:8080")
```

## 7. 常见警告处理

### ffmpeg警告
```bash
RuntimeWarning: Couldn't find ffmpeg or avconv
```

**解决方案（可选）：**
```bash
sudo apt install ffmpeg -y
```

### jieba兼容性警告
```bash
UserWarning: pkg_resources is deprecated
```

**解决方案（可选）：**
```bash
pip install --upgrade setuptools
```

### 静态文件警告
```bash
staticfiles.W004: The directory '/ui/dist/admin' does not exist
```

**解决方案（可选）：**
```bash
cd ui/
npm install
npm run build
```

## 8. 调试技巧

### 查看详细错误信息
```bash
python apps/manage.py check --verbosity=2
python apps/manage.py migrate --verbosity=2
```

### 测试特定模块导入
```bash
python -c "import [module_name]; print('导入成功')"
```

### 查看Django配置
```bash
python apps/manage.py diffsettings
```

### 数据库连接测试
```bash
python apps/manage.py dbshell
```

## 9. 环境检查清单

部署前检查：
- [ ] Python虚拟环境已激活
- [ ] 设置了 `MAXKB_CONFIG=1` 环境变量
- [ ] `config.yml` 文件存在且配置正确
- [ ] `/opt/maxkb` 目录权限正确
- [ ] 数据库连接正常
- [ ] 所有Python依赖已安装
- [ ] 迁移冲突已解决

## 10. 性能优化建议

### 依赖安装优化
```bash
# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 使用CPU版本PyTorch（减少下载大小）
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### 数据库连接池配置
```yaml
# config.yml
DB_MAX_OVERFLOW: 20  # 根据并发需求调整
```

### 开发环境配置
```yaml
DEBUG: true
LOG_LEVEL: 'INFO'
```

## 11. 总结

MaxKB本地开发环境配置的核心要点：

1. **环境隔离**：必须使用Python虚拟环境
2. **配置路径**：设置 `MAXKB_CONFIG=1` 环境变量
3. **权限管理**：确保 `/opt/maxkb` 目录权限
4. **数据库配置**：使用正确的连接池后端
5. **依赖管理**：一次性安装完整依赖列表
6. **迁移处理**：遇到冲突使用 `--merge` 参数
7. **启动方式**：推荐直接使用Django命令启动

遵循这些要点，可以避免大部分常见问题，快速建立稳定的开发环境。