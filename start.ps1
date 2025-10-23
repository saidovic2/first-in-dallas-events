# Start script for Local Event CMS
Write-Host "Starting Local Event CMS..." -ForegroundColor Green

# Check if containers exist
$containers = docker-compose ps -q
if (-not $containers) {
    Write-Host "Containers not found. Running setup..." -ForegroundColor Yellow
    .\setup.ps1
    exit 0
}

# Start all services
Write-Host "`nStarting all services..." -ForegroundColor Yellow
docker-compose up -d

Write-Host "`n✓ Services started!" -ForegroundColor Green
Write-Host "`nAccess the application at:" -ForegroundColor Cyan
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "  API: http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "`nTo view logs: docker-compose logs -f" -ForegroundColor Yellow
Write-Host "To stop: docker-compose down" -ForegroundColor Yellow
