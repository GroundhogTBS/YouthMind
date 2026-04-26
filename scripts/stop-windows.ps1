# stop-windows.ps1
# YouthMind Windows停止脚本

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  YouthMind 服务停止脚本 (Windows)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

pm2 stop all

Write-Host ""
Write-Host "所有服务已停止" -ForegroundColor Green
pm2 status
