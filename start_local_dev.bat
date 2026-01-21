@echo off
chcp 65001 >nul
echo ========================================
echo MaxKB 本地开发环境一键启动
echo ========================================
echo.

echo [检查] Docker是否运行...
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker未运行！请先启动Docker Desktop
    pause
    exit /b 1
)
echo ✅ Docker运行正常
echo.

echo [1/4] 启动PostgreSQL容器（带pgvector）...
docker ps -a | findstr maxkb-postgres >nul 2>&1
if %errorlevel% equ 0 (
    echo 容器已存在，正在启动...
    docker start maxkb-postgres
) else (
    echo 创建新容器...
    docker run -d --name maxkb-postgres ^
      -e POSTGRES_USER=root ^
      -e POSTGRES_PASSWORD=Password123@postgres ^
      -e POSTGRES_DB=maxkb ^
      -p 5432:5432 ^
      pgvector/pgvector:pg17
)

if %errorlevel% neq 0 (
    echo ❌ PostgreSQL启动失败！
    pause
    exit /b 1
)
echo ✅ PostgreSQL启动成功
echo.

echo [2/4] 启动Redis容器...
docker ps -a | findstr maxkb-redis >nul 2>&1
if %errorlevel% equ 0 (
    echo 容器已存在，正在启动...
    docker start maxkb-redis
) else (
    echo 创建新容器...
    docker run -d --name maxkb-redis ^
      -p 6379:6379 ^
      redis:latest redis-server --requirepass Password123@redis
)

if %errorlevel% neq 0 (
    echo ❌ Redis启动失败！
    pause
    exit /b 1
)
echo ✅ Redis启动成功
echo.

echo [3/4] 等待数据库就绪...
timeout /t 5 /nobreak >nul
echo ✅ 数据库就绪
echo.

echo [4/4] 运行数据库迁移...
python main.py upgrade_db

if %errorlevel% neq 0 (
    echo.
    echo ❌ 数据库迁移失败！
    echo 可能的原因：
    echo 1. Python依赖未安装（运行: pip install uv ^&^& python -m uv pip install -r pyproject.toml）
    echo 2. 数据库连接失败
    echo 3. .env配置错误
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ 环境启动成功！
echo ========================================
echo.
echo 📊 服务信息:
echo   - PostgreSQL: localhost:5432
echo   - Redis: localhost:6379
echo   - MaxKB后端: http://localhost:8080
echo.
echo 🔑 默认账号:
echo   - 用户名: admin
echo   - 密码: MaxKB@123..
echo.
echo 🚀 正在启动MaxKB开发服务器...
echo    按 Ctrl+C 停止服务器
echo.
echo ========================================
echo.

python main.py dev web

pause

