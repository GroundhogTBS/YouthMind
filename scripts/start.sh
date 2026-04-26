#!/bin/bash

echo "=========================================="
echo "  YouthMind 服务启动脚本"
echo "=========================================="

# 加载环境变量
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "错误: .env 文件不存在，请先创建环境变量文件"
    exit 1
fi

# 创建日志目录
mkdir -p logs

# 检查依赖
check_dependencies() {
    echo "检查依赖..."
    
    # 检查 Node.js
    if ! command -v node &> /dev/null; then
        echo "错误: Node.js 未安装"
        exit 1
    fi
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        echo "错误: Python3 未安装"
        exit 1
    fi
    
    # 检查 PM2
    if ! command -v pm2 &> /dev/null; then
        echo "安装 PM2..."
        npm install -g pm2
    fi
    
    echo "依赖检查通过"
}

# 安装后端依赖
install_backend_deps() {
    echo "安装后端依赖..."
    
    if [ -d "backend/services/core-service" ]; then
        cd backend/services/core-service && npm install && cd ../../..
    fi
    
    if [ -d "backend/services/chat-service" ]; then
        cd backend/services/chat-service && npm install && cd ../../..
    fi
    
    if [ -d "backend/services/alert-service" ]; then
        cd backend/services/alert-service && npm install && cd ../../..
    fi
    
    echo "后端依赖安装完成"
}

# 安装AI服务依赖
install_ai_deps() {
    echo "安装AI服务依赖..."
    
    if [ -d "ai-service" ]; then
        cd ai-service
        if [ ! -d "venv" ]; then
            python3 -m venv venv
        fi
        source venv/bin/activate
        pip install -r requirements.txt
        deactivate
        cd ..
    fi
    
    echo "AI服务依赖安装完成"
}

# 启动服务
start_services() {
    echo "启动服务..."
    
    # 使用PM2启动服务
    if [ -f "ecosystem.config.js" ]; then
        pm2 start ecosystem.config.js
    else
        # 手动启动各服务
        cd backend/services/core-service && pm2 start npm --name core-service -- run start:prod && cd ../../..
        cd backend/services/chat-service && pm2 start npm --name chat-service -- run start:prod && cd ../../..
        cd backend/services/alert-service && pm2 start npm --name alert-service -- run start:prod && cd ../../..
        
        # 启动AI服务
        if [ -d "ai-service" ]; then
            cd ai-service
            source venv/bin/activate
            pm2 start venv/bin/uvicorn --name ai-service -- main:app --host 0.0.0.0 --port 9001
            deactivate
            cd ..
        fi
    fi
    
    echo "服务启动完成"
}

# 显示状态
show_status() {
    echo ""
    echo "=========================================="
    echo "  服务状态"
    echo "=========================================="
    pm2 status
    echo ""
    echo "访问地址:"
    echo "  - 青少年端: http://localhost"
    echo "  - 管理后台: http://localhost/admin"
    echo "  - Core API: http://localhost:8001"
    echo "  - Chat API: http://localhost:8002"
    echo "  - Alert API: http://localhost:8003"
    echo "  - AI Service: http://localhost:9001"
    echo ""
}

# 主流程
main() {
    check_dependencies
    install_backend_deps
    install_ai_deps
    start_services
    show_status
}

main
