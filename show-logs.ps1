# Show all logs
Write-Host "=== DATABASE LOGS ===" -ForegroundColor Cyan
docker-compose logs --tail=20 db
Write-Host ""

Write-Host "=== API LOGS ===" -ForegroundColor Cyan
docker-compose logs --tail=50 api
Write-Host ""

Write-Host "=== WEB LOGS ===" -ForegroundColor Cyan
docker-compose logs --tail=20 web
Write-Host ""

Write-Host "=== CONTAINER STATUS ===" -ForegroundColor Cyan
docker-compose ps
