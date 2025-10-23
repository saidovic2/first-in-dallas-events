# Rebuild Script - Fix Docker Build Issues
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Rebuilding Local Event CMS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Step 1: Stopping all services..." -ForegroundColor Yellow
docker-compose down
Write-Host "✓ Services stopped" -ForegroundColor Green
Write-Host ""

Write-Host "Step 2: Removing old images..." -ForegroundColor Yellow
docker-compose rm -f
Write-Host "✓ Old containers removed" -ForegroundColor Green
Write-Host ""

Write-Host "Step 3: Rebuilding containers (this may take 5-10 minutes)..." -ForegroundColor Yellow
docker-compose build --no-cache
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Build failed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Common fixes:" -ForegroundColor Yellow
    Write-Host "  1. Make sure Docker Desktop is running" -ForegroundColor White
    Write-Host "  2. Restart Docker Desktop" -ForegroundColor White
    Write-Host "  3. Check your internet connection" -ForegroundColor White
    exit 1
}
Write-Host "✓ Build complete" -ForegroundColor Green
Write-Host ""

Write-Host "Step 4: Starting services..." -ForegroundColor Yellow
docker-compose up -d
Write-Host "✓ Services started" -ForegroundColor Green
Write-Host ""

Write-Host "Step 5: Waiting for services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 30
Write-Host ""

Write-Host "Step 6: Checking status..." -ForegroundColor Yellow
docker-compose ps
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Rebuild Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access your application at:" -ForegroundColor Yellow
Write-Host "  Frontend: http://localhost:3001" -ForegroundColor Cyan
Write-Host "  API: http://localhost:8001" -ForegroundColor Cyan
Write-Host "  API Docs: http://localhost:8001/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Login credentials:" -ForegroundColor Yellow
Write-Host "  Email: admin@example.com" -ForegroundColor White
Write-Host "  Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "Note: Wait 1-2 minutes for Next.js to compile" -ForegroundColor Gray
Write-Host ""
