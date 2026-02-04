#!/bin/bash

# 启动后端服务
echo "Starting backend service..."
python main.py start all

echo "Backend service started."
echo "Backend API will be available at http://localhost:8080"