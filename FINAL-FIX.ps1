# FINAL FIX - Complete Reset
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  COMPLETE SYSTEM RESET" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "This will:" -ForegroundColor Yellow
Write-Host "  1. Stop all services" -ForegroundColor White
Write-Host "  2. Remove containers and volumes" -ForegroundColor White
Write-Host "  3. Rebuild everything" -ForegroundColor White
Write-Host "  4. Start fresh" -ForegroundColor White
Write-Host ""
Write-Host "This will take 5-10 minutes." -ForegroundColor Yellow
Write-Host ""

$confirm = Read-Host "Continue? (y/n)"
if ($confirm -ne "y") {
    Write-Host "Cancelled" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Step 1/5: Stopping all services..." -ForegroundColor Yellow
docker-compose down -v
Write-Host "Done" -ForegroundColor Green
Write-Host ""

Write-Host "Step 2/5: Cleaning up..." -ForegroundColor Yellow
docker system prune -f
Write-Host "Done" -ForegroundColor Green
Write-Host ""

Write-Host "Step 3/5: Rebuilding (this takes time)..." -ForegroundColor Yellow
docker-compose build --no-cache
Write-Host "Done" -ForegroundColor Green
Write-Host ""

Write-Host "Step 4/5: Starting services..." -ForegroundColor Yellow
docker-compose up -d
Write-Host "Done" -ForegroundColor Green
Write-Host ""

Write-Host "Step 5/5: Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 60
Write-Host "Done" -ForegroundColor Green
Write-Host ""

Write-Host "Checking status..." -ForegroundColor Yellow
docker-compose ps
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RESET COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Wait 2 more minutes, then go to:" -ForegroundColor Yellow
Write-Host "  http://localhost:3001" -ForegroundColor Cyan
Write-Host ""
Write-Host "Login:" -ForegroundColor Yellow
Write-Host "  admin@example.com / admin123" -ForegroundColor White
Write-Host ""
