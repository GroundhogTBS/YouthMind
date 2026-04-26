@echo off
echo ========================================
echo YouthMind 服务启动脚本
echo ========================================

echo.
echo [1/3] 启动 AI 服务...
start "AI Service" cmd /k "cd /d %~dp0ai-service\unified-ai-service && .\venv\Scripts\activate && python main.py"

timeout /t 3 /nobreak > nul

echo [2/3] 启动后端 API 服务...
start "API Service" cmd /k "cd /d %~dp0backend\api && npm run start:dev"

timeout /t 3 /nobreak > nul

echo [3/3] 启动前端...
start "Frontend" cmd /k "cd /d %~dp0frontend\teen-app && npm run dev"

echo.
echo ========================================
echo 所有服务已启动！
echo ========================================
echo.
echo 前端: http://localhost:3001
echo 后端API: http://localhost:8000/api
echo AI服务: http://localhost:9000/docs
echo.
pause
