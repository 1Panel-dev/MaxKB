# MaxKB 本地开发部署文档

## 环境要求

- 操作系统：Windows + WSL 2
- Python：3.11+
- Node.js：16+（前端构建）
- PostgreSQL：数据库
- Redis：缓存和消息队列

## 1. 环境准备

### 1.1 WSL环境配置

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python和基础工具
sudo apt install python3 python3-pip python3-venv python3-dev -y

# 安装PostgreSQL客户端（用于连接远程数据库）
sudo apt install postgresql-client -y
```

### 1.2 创建Python虚拟环境

```bash
# 进入项目目录
cd /mnt/d/GitRepo/MokeKB

# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate
```

## 2. 依赖安装

### 2.1 安装Python依赖

```bash
# 使用项目提供的requirements.txt
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 如果PyTorch安装有问题，单独处理
pip install torch==2.8.0 --index-url https://download.pytorch.org/whl/cpu
```

### 2.2 创建必要的系统目录

```bash
# 创建MaxKB运行所需的目录
sudo mkdir -p /opt/maxkb/{logs,local,conf}
sudo chown -R $USER:$USER /opt/maxkb
```

## 3. 配置文件设置

### 3.1 复制配置模板

```bash
# 复制配置文件模板
cp config_example.yml config.yml
```

### 3.2 编辑配置文件

```yaml
# config.yml 关键配置项

# 数据库配置
DB_NAME: your_db_name
DB_HOST: your_db_host
DB_PORT: 5432
DB_USER: your_db_user
DB_PASSWORD: your_db_password
DB_ENGINE: dj_db_conn_pool.backends.postgresql  # 注意使用连接池版本

# Redis配置
REDIS_HOST: '127.0.0.1'
REDIS_PORT: 6379
REDIS_PASSWORD: 'your_redis_password'
REDIS_DB: 0

# 基础配置
DEBUG: true
LOG_LEVEL: 'INFO'
TIME_ZONE: 'Asia/Shanghai'
LANGUAGE_CODE: 'zh-CN'
```

### 3.3 设置环境变量

```bash
# 让程序从项目根目录读取配置文件
export MAXKB_CONFIG=1

# 可以添加到 ~/.bashrc 中永久生效
echo 'export MAXKB_CONFIG=1' >> ~/.bashrc
```

## 4. 数据库初始化

### 4.1 验证数据库连接

```bash
# 测试数据库连接
python apps/manage.py check --database
```

### 4.2 处理迁移冲突（如果存在）

```bash
# 查看迁移状态
python apps/manage.py showmigrations

# 如果有冲突，合并迁移
python apps/manage.py makemigrations --merge

# 执行迁移
python apps/manage.py migrate
```

## 5. 启动服务

### 5.1 方式1：使用Django开发服务器（推荐）

```bash
cd /mnt/d/GitRepo/MokeKB
export MAXKB_CONFIG=1
python apps/manage.py runserver 0.0.0.0:8080
```

### 5.2 方式2：使用项目启动脚本

```bash
cd /mnt/d/GitRepo/MokeKB
export MAXKB_CONFIG=1
python main.py dev web
```

### 5.3 验证服务

访问 http://localhost:8080 验证服务是否正常运行。

## 6. PyCharm IDE配置

### 6.1 配置Python解释器

1. 打开PyCharm → File → Settings → Project → Python Interpreter
2. 选择 WSL → 选择WSL发行版
3. Python解释器路径：`/mnt/d/GitRepo/MokeKB/.venv/bin/python`

### 6.2 配置Django项目

1. Settings → Languages & Frameworks → Django
2. 勾选 "Enable Django Support"
3. Django project root: `/mnt/d/GitRepo/MokeKB/apps`
4. Settings: `maxkb/settings.py`
5. Manage script: `/mnt/d/GitRepo/MokeKB/apps/manage.py`

### 6.3 创建运行配置

1. Run → Edit Configurations → Django Server
2. Host: 127.0.0.1, Port: 8080
3. Working directory: `/mnt/d/GitRepo/MokeKB/apps`

## 7. 可选：前端构建

```bash
# 构建前端界面（可选）
cd /mnt/d/GitRepo/MokeKB/ui
npm install
npm run build
```

## 8. 常用命令

```bash
# 激活环境
source .venv/bin/activate
export MAXKB_CONFIG=1

# 检查配置
python apps/manage.py check

# 数据库操作
python apps/manage.py migrate
python apps/manage.py showmigrations

# 创建超级用户
python apps/manage.py createsuperuser

# 启动服务
python apps/manage.py runserver 0.0.0.0:8080
```

## 9. 注意事项

1. **配置文件路径**：确保设置了 `MAXKB_CONFIG=1` 环境变量
2. **数据库引擎**：必须使用 `dj_db_conn_pool.backends.postgresql`
3. **权限问题**：确保 `/opt/maxkb` 目录有写入权限
4. **依赖冲突**：如果遇到依赖问题，可以分批安装核心依赖
5. **迁移冲突**：使用 `makemigrations --merge` 解决迁移冲突

## 10. 故障排除

参考 `troubleshooting-guide.md` 文档了解常见问题的解决方案。