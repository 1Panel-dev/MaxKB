#!/bin/bash

# 启动前端管理界面
echo "Starting frontend admin interface..."
cd ui && npm run dev &

# 启动前端聊天界面
echo "Starting frontend chat interface..."
cd ui && npm run chat &

echo "Frontend interfaces started."
echo "Admin interface will be available at http://localhost:3000"
echo "Make sure the backend service is running at http://localhost:8080"
echo "Press Ctrl+C to stop both interfaces."

# 等待所有后台任务完成
wait