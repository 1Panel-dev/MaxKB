# 回到根目录
```shell
cd ../../
```

# 安装 virtualenv
```shell
pip install virtualenv
```

# 创建虚拟环境
```shell
python -m venv venv
```

# 激活虚拟环境 (Windows)
```shell
venv\Scripts\activate
```



# 安装 uv (推荐的 Python 包管理器)
```shell
pip install uv
```

# 使用 uv 安装项目依赖
```shell
uv pip install -e .
```



# 创建 .env 文件
```shell
@echo off
chcp 65001 >nul
setlocal
cd ../../
:: 检查 .env 是否已经存在
if exist ".env" (
    echo ==============================================
    echo 提示：.env 文件已存在，无需重复创建
    echo ==============================================
    pause >nul
    exit /b
)

:: 文件不存在，开始创建并写入内容
echo ==============================================
echo 正在生成 .env 配置文件...
echo ==============================================

:: 先创建空文件
type nul > .env

:: 写入自定义环境变量，自行修改这里的内容即可
echo.> .env
echo # 数据库配置> .env
echo MAXKB_DB_NAME=maxkb>> .env
echo MAXKB_DB_HOST=127.0.0.1>> .env
echo MAXKB_DB_PORT=5432>> .env
echo MAXKB_DB_USER=root>> .env
echo MAXKB_DB_PASSWORD=Password123@postgres>> .env
echo.>> .env
echo # Redis 配置>> .env
echo MAXKB_REDIS_HOST=127.0.0.1>> .env
echo MAXKB_REDIS_PORT=6379>> .env
echo MAXKB_REDIS_PASSWORD=Password123@redis>> .env
echo MAXKB_REDIS_DB=0>> .env
echo MAXKB_REDIS_MAX_CONNECTIONS=100>> .env
echo.>> .env
echo # 其他配置>> .env
echo MAXKB_CONFIG_TYPE=ENV>> .env
echo MAXKB_DEBUG=True>> .env
echo MAXKB_LANGUAGE_CODE=zh-CN>> .env
echo MAXKB_TIME_ZONE=Asia/Shanghai>> .env

echo.
echo ✅ .env 文件创建并初始化完成，请按实际情况进行修改！
echo.
pause >nul
```
