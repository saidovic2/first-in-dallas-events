# Fix API Issues
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Fixing API Backend" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Step 1: Checking current status..." -ForegroundColor Yellow
docker-compose ps api
Write-Host ""

Write-Host "Step 2: Restarting database..." -ForegroundColor Yellow
docker-compose restart db
Start-Sleep -Seconds 10
Write-Host "✓ Database restarted" -ForegroundColor Green
Write-Host ""

Write-Host "Step 3: Initializing database..." -ForegroundColor Yellow
docker-compose exec -T api python init_db.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Database initialized" -ForegroundColor Green
} else {
    Write-Host "⚠ Database initialization had issues (may be normal if already initialized)" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "Step 4: Restarting API..." -ForegroundColor Yellow
docker-compose restart api
Start-Sleep -Seconds 10
Write-Host "✓ API restarted" -ForegroundColor Green
Write-Host ""

Write-Host "Step 5: Testing API..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/health" -TimeoutSec 10 -ErrorAction Stop
    Write-Host "✓ API is working!" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor White
} catch {
    Write-Host "✗ API still not responding" -ForegroundColor Red
    Write-Host ""
    Write-Host "Checking API logs..." -ForegroundColor Yellow
    docker-compose logs --tail=30 api
    Write-Host ""
    Write-Host "Try rebuilding API:" -ForegroundColor Yellow
    Write-Host "  docker-compose up -d --build api" -ForegroundColor White
    exit 1
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  API Fixed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Now try logging in at: http://localhost:3001" -ForegroundColor Cyan
Write-Host ""
Write-Host "Credentials:" -ForegroundColor Yellow
Write-Host "  Email: admin@example.com" -ForegroundColor White
Write-Host "  Password: admin123" -ForegroundColor White
Write-Host ""
