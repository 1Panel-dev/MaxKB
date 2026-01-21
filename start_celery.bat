@echo off
chcp 65001 >nul
echo ========================================
echo MaxKB Celery Worker (Windows)
echo ========================================
echo.
echo 注意：请先启动 Web 服务（运行 start_dev.bat）
echo.

REM 检查虚拟环境
if exist venv\Scripts\activate.bat (
    echo [1/2] 激活虚拟环境...
    call venv\Scripts\activate.bat
) else (
    echo [警告] 未找到虚拟环境，使用系统 Python
)

echo.
echo [2/2] 启动 Celery 任务队列...
echo.
echo Celery 用于处理异步任务：
echo - 文档向量化
echo - 定时任务
echo - 后台处理
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

python main.py dev celery

echo.
echo ========================================
echo Celery 已停止
echo ========================================
pause

