#!/bin/bash

echo "=========================================="
echo "  YouthMind 服务停止脚本"
echo "=========================================="

# 停止所有PM2进程
pm2 stop all

# 停止Nginx（如果需要）
# sudo systemctl stop nginx

echo ""
echo "所有服务已停止"
pm2 status
