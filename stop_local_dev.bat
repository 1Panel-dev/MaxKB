@echo off
chcp 65001 >nul
echo ========================================
echo MaxKB 本地开发环境停止
echo ========================================
echo.

echo [1/2] 停止PostgreSQL容器...
docker stop maxkb-postgres >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ PostgreSQL已停止
) else (
    echo ⚠️  PostgreSQL容器未运行或不存在
)

echo [2/2] 停止Redis容器...
docker stop maxkb-redis >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Redis已停止
) else (
    echo ⚠️  Redis容器未运行或不存在
)

echo.
echo ========================================
echo ✅ 环境已停止
echo ========================================
echo.
echo 💡 提示:
echo   - 重新启动: 运行 start_local_dev.bat
echo   - 删除容器: docker rm maxkb-postgres maxkb-redis
echo   - 删除数据: docker volume prune
echo.

pause

