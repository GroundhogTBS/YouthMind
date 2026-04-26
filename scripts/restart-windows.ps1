# restart-windows.ps1
# YouthMind Windows重启脚本

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  YouthMind 服务重启脚本 (Windows)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

pm2 restart all

Write-Host ""
Write-Host "所有服务已重启" -ForegroundColor Green
pm2 status
