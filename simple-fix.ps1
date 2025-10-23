# Simple Fix Script
Write-Host "Fixing API..." -ForegroundColor Yellow
Write-Host ""

# Check what's running
Write-Host "Current status:" -ForegroundColor Cyan
docker-compose ps
Write-Host ""

# Show API logs
Write-Host "API Logs (last 30 lines):" -ForegroundColor Cyan
docker-compose logs --tail=30 api
Write-Host ""

# Restart everything in order
Write-Host "Restarting services..." -ForegroundColor Yellow
docker-compose restart db redis
Start-Sleep -Seconds 15

docker-compose restart api
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "Testing API..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

$result = docker-compose exec -T api curl -s http://localhost:8000/health 2>&1
Write-Host "API Response: $result"
Write-Host ""

Write-Host "Done! Try logging in now at http://localhost:3001" -ForegroundColor Green
