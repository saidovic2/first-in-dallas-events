# Check API Status
Write-Host "Checking API Status..." -ForegroundColor Yellow
Write-Host ""

# Check if API container is running
Write-Host "1. Checking API container..." -ForegroundColor Cyan
$apiStatus = docker-compose ps api
Write-Host $apiStatus
Write-Host ""

# Check API logs
Write-Host "2. Checking API logs (last 20 lines)..." -ForegroundColor Cyan
docker-compose logs --tail=20 api
Write-Host ""

# Try to connect to API
Write-Host "3. Testing API connection..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✓ API is responding!" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor White
} catch {
    Write-Host "✗ API is not responding" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Possible fixes:" -ForegroundColor Yellow
    Write-Host "  1. Restart API: docker-compose restart api" -ForegroundColor White
    Write-Host "  2. Check logs: docker-compose logs -f api" -ForegroundColor White
    Write-Host "  3. Rebuild API: docker-compose up -d --build api" -ForegroundColor White
}
Write-Host ""

# Check database connection
Write-Host "4. Checking database..." -ForegroundColor Cyan
$dbStatus = docker-compose ps db
Write-Host $dbStatus
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Run this to fix API issues:" -ForegroundColor Yellow
Write-Host "  docker-compose restart api" -ForegroundColor White
Write-Host "  docker-compose logs -f api" -ForegroundColor White
Write-Host ""
