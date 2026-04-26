@echo off
echo ========================================
echo YouthMind 服务停止脚本
echo ========================================

echo 停止所有 Node.js 进程...
taskkill /F /IM node.exe 2>nul

echo 停止所有 Python 进程...
taskkill /F /IM python.exe 2>nul

echo.
echo 所有服务已停止。
pause
