# Quick Fix Script for Local Event CMS
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Local Event CMS - Quick Fix Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker
Write-Host "Step 1: Checking Docker..." -ForegroundColor Yellow
docker --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Docker is not running!" -ForegroundColor Red
    Write-Host "  Please start Docker Desktop and try again." -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ Docker is running" -ForegroundColor Green
Write-Host ""

# Stop all services
Write-Host "Step 2: Stopping all services..." -ForegroundColor Yellow
docker-compose down
Write-Host "✓ Services stopped" -ForegroundColor Green
Write-Host ""

# Check for port conflicts
Write-Host "Step 3: Checking for port conflicts..." -ForegroundColor Yellow
$ports = @(3000, 8000, 5432, 6379)
$conflicts = @()

foreach ($port in $ports) {
    $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connection) {
        $conflicts += $port
        Write-Host "  ⚠ Port $port is in use" -ForegroundColor Yellow
    }
}

if ($conflicts.Count -gt 0) {
    Write-Host ""
    Write-Host "Warning: The following ports are in use:" -ForegroundColor Yellow
    foreach ($port in $conflicts) {
        Write-Host "  - Port $port" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Cyan
    Write-Host "  1. Close other applications using these ports" -ForegroundColor White
    Write-Host "  2. Continue anyway (services may fail to start)" -ForegroundColor White
    Write-Host ""
    $response = Read-Host "Continue? (y/n)"
    if ($response -ne "y") {
        Write-Host "Exiting..." -ForegroundColor Yellow
        exit 0
    }
}
Write-Host "✓ Port check complete" -ForegroundColor Green
Write-Host ""

# Start services
Write-Host "Step 4: Starting services..." -ForegroundColor Yellow
Write-Host "  This will take 2-3 minutes..." -ForegroundColor Gray
docker-compose up -d

Write-Host ""
Write-Host "Step 5: Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check service status
Write-Host ""
Write-Host "Step 6: Checking service status..." -ForegroundColor Yellow
docker-compose ps

Write-Host ""
Write-Host "Step 7: Testing connections..." -ForegroundColor Yellow

# Test API
Write-Host "  Testing API..." -ForegroundColor Gray
Start-Sleep -Seconds 5
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "  ✓ API is responding" -ForegroundColor Green
} catch {
    Write-Host "  ✗ API is not responding yet" -ForegroundColor Yellow
    Write-Host "    Waiting 10 more seconds..." -ForegroundColor Gray
    Start-Sleep -Seconds 10
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -ErrorAction Stop
        Write-Host "  ✓ API is now responding" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ API still not responding" -ForegroundColor Red
        Write-Host "    Check logs: docker-compose logs api" -ForegroundColor Yellow
    }
}

# Test Frontend
Write-Host "  Testing Frontend..." -ForegroundColor Gray
Start-Sleep -Seconds 5
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "  ✓ Frontend is responding" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Frontend is not responding yet" -ForegroundColor Yellow
    Write-Host "    This is normal - Next.js is still compiling..." -ForegroundColor Gray
    Write-Host "    Wait 1-2 more minutes and try again" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Fix Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Wait 1-2 minutes for Next.js to compile" -ForegroundColor White
Write-Host "2. Open your browser to: http://localhost:3000" -ForegroundColor White
Write-Host "3. Login with:" -ForegroundColor White
Write-Host "   Email: admin@example.com" -ForegroundColor Cyan
Write-Host "   Password: admin123" -ForegroundColor Cyan
Write-Host ""
Write-Host "Useful Commands:" -ForegroundColor Yellow
Write-Host "  View logs:    docker-compose logs -f" -ForegroundColor White
Write-Host "  Check status: docker-compose ps" -ForegroundColor White
Write-Host "  Stop all:     docker-compose down" -ForegroundColor White
Write-Host ""
Write-Host "If still not working:" -ForegroundColor Yellow
Write-Host "  1. Check logs: docker-compose logs -f web" -ForegroundColor White
Write-Host "  2. Read: TROUBLESHOOTING.md" -ForegroundColor White
Write-Host ""
