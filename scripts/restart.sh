#!/bin/bash

echo "=========================================="
echo "  YouthMind 服务重启脚本"
echo "=========================================="

# 重启所有PM2进程
pm2 restart all

# 重启Nginx（如果需要）
# sudo systemctl restart nginx

echo ""
echo "所有服务已重启"
pm2 status
