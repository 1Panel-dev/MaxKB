# maxkb

## 1 项目结构

!!! Abstract ""

```
.
├── LICENSE # License 申明
├── README.md
├── apps #   后端项目根目录
│ ├── common    # 项目公共资源目录
│ ├── smartdoc  # 项目主目录 
│ ├── users     # 用户相关
│ ├── manage.py #  django项目入口
│ └── sdk # 项目通用的前后端依赖/网关的前端
├── pyproject.toml # 后端依赖 配置文件
└── ui # 前端项目根目录
├── config_example.yml # 项目配置示例 
├── main.py            # 项目入口文件 python main.py start 启动项目
```

## 2 环境准备

### 1 前端环境准备

- 安装 [node](https://nodejs.org/)

### 2 后端环境准备

- 安装 [python](https://www.python.org/downloads/release/python-3115/)
- 安装 [pycharm](https://www.jetbrains.com/pycharm/download/)

### 3 开发环境搭建

#### 安装poetry包管理器

!!! Abstract ""

``` bash
pip install poetry
```

# 3 开发准备

### 3.2 本地配置

!!! Abstract ""
若要项目启动，需要准备配置文件及目录

- 准备配置文件
   ```bash
   #将config_example.yml配置文件 目录拷贝至 /opt/maxkb/conf目录下
   cp config_example.yml /opt/maxkb/conf
   ```
    - 配置`/opt/maxkb/conf/config_example.yml`
   ```
    # 邮箱配置
    EMAIL_ADDRESS: xxx
    EMAIL_USE_TLS: False
    EMAIL_USE_SSL: True
    EMAIL_HOST: smtp.qq.com
    EMAIL_PORT: 465
    EMAIL_HOST_USER:
    EMAIL_HOST_PASSWORD:
    # 数据库配置 
    DB_NAME: smart-doc
    DB_HOST: localhost
    DB_PORT: 5432
    DB_USER: root
    DB_PASSWORD: xxx
    DB_ENGINE: django.db.backends.postgresql_psycopg2
   ```

# 4 开发调试

## 4.1 启动前端项目

先在ui执行安装前端需要的依赖

```bash
npm install
```

启动项目

``` bash
npm run dev
```

## 启动后端项目

### 4.2 启动后端项目

!!! Abstract ""
先在根目录执行安装后端需要的依赖

```bash
poetry install
```

启动项目

``` bash
python main.py start
```
 