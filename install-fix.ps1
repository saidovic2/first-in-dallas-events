# Install Missing Package
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Installing Missing Package" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Installing email-validator in API container..." -ForegroundColor Yellow
docker-compose exec -T api pip install email-validator==2.1.0
Write-Host ""

Write-Host "Restarting API..." -ForegroundColor Yellow
docker-compose restart api
Write-Host ""

Write-Host "Waiting for API to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 15
Write-Host ""

Write-Host "Testing API..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/health" -TimeoutSec 10
    Write-Host "✓ API is working!" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor White
} catch {
    Write-Host "Still having issues. Checking logs..." -ForegroundColor Yellow
    docker-compose logs --tail=20 api
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Done!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Try logging in at: http://localhost:3001" -ForegroundColor Cyan
Write-Host "Email: admin@example.com" -ForegroundColor White
Write-Host "Password: admin123" -ForegroundColor White
Write-Host ""
