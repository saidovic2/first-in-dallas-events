# Stop script for Local Event CMS
Write-Host "Stopping Local Event CMS..." -ForegroundColor Yellow

docker-compose down

Write-Host "`n✓ All services stopped" -ForegroundColor Green
