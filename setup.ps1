# Setup script for Local Event CMS
Write-Host "Setting up Local Event CMS..." -ForegroundColor Green

# Check if Docker is running
Write-Host "`nChecking Docker..." -ForegroundColor Yellow
docker --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Docker is not installed or not running" -ForegroundColor Red
    exit 1
}

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "`nCreating .env file..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✓ .env file created" -ForegroundColor Green
}

# Build and start containers
Write-Host "`nBuilding Docker containers..." -ForegroundColor Yellow
docker-compose build

Write-Host "`nStarting services..." -ForegroundColor Yellow
docker-compose up -d db redis

# Wait for database to be ready
Write-Host "`nWaiting for database to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Start API and worker
docker-compose up -d api worker

# Wait for API to be ready
Write-Host "`nWaiting for API to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start web frontend
Write-Host "`nStarting web frontend..." -ForegroundColor Yellow
docker-compose up -d web

Write-Host "`n✓ Setup complete!" -ForegroundColor Green
Write-Host "`nServices are starting up. Please wait a moment..." -ForegroundColor Yellow
Write-Host "`nAccess the application at:" -ForegroundColor Cyan
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "  API: http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "`nDefault login credentials:" -ForegroundColor Cyan
Write-Host "  Email: admin@example.com" -ForegroundColor White
Write-Host "  Password: admin123" -ForegroundColor White
Write-Host "`nTo view logs: docker-compose logs -f" -ForegroundColor Yellow
Write-Host "To stop: docker-compose down" -ForegroundColor Yellow
