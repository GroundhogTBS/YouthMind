# start-windows.ps1
# YouthMind Windows启动脚本

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  YouthMind 服务启动脚本 (Windows)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 检查Node.js
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "错误: Node.js 未安装" -ForegroundColor Red
    Write-Host "请访问 https://nodejs.org/ 下载安装" -ForegroundColor Yellow
    exit 1
}

# 检查Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "错误: Python 未安装" -ForegroundColor Red
    Write-Host "请访问 https://www.python.org/ 下载安装" -ForegroundColor Yellow
    exit 1
}

# 检查PM2
if (-not (Get-Command pm2 -ErrorAction SilentlyContinue)) {
    Write-Host "安装 PM2..." -ForegroundColor Yellow
    npm install -g pm2
}

# 创建日志目录
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

# 加载环境变量
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.*)$") {
            [Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), "Process")
        }
    }
} else {
    Write-Host "警告: .env 文件不存在，使用默认配置" -ForegroundColor Yellow
}

# 启动服务
Write-Host "启动服务..." -ForegroundColor Green

# 使用PM2启动
pm2 start ecosystem.config.js

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  服务状态" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
pm2 status

Write-Host ""
Write-Host "访问地址:" -ForegroundColor Green
Write-Host "  - 青少年端: http://localhost:5173" -ForegroundColor White
Write-Host "  - 管理后台: http://localhost:5174" -ForegroundColor White
Write-Host "  - Core API: http://localhost:8001" -ForegroundColor White
Write-Host "  - Chat API: http://localhost:8002" -ForegroundColor White
Write-Host "  - Alert API: http://localhost:8003" -ForegroundColor White
Write-Host "  - AI Service: http://localhost:9001" -ForegroundColor White
Write-Host ""
