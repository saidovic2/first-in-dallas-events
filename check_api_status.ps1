# Quick API Health Check

$API_URL = "https://wonderful-vibrancy-production.up.railway.app"

Write-Host "🔍 Checking API status..." -ForegroundColor Cyan
Write-Host ""

# Check if API is running
try {
    $response = Invoke-WebRequest -Uri "$API_URL/docs" -Method GET -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ API is running!" -ForegroundColor Green
        Write-Host "   Docs available at: $API_URL/docs" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ API is not responding" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "🔍 Checking Dallas Arboretum endpoint..." -ForegroundColor Cyan

# Check if the dallas-arboretum endpoint exists (it will return 401 without auth)
try {
    $response = Invoke-WebRequest -Uri "$API_URL/api/sync/dallas-arboretum" -Method POST -TimeoutSec 10 -SkipHttpErrorCheck
    
    if ($response.StatusCode -eq 401 -or $response.StatusCode -eq 422 -or $response.StatusCode -eq 403) {
        Write-Host "✅ Dallas Arboretum endpoint exists (returned auth error as expected)" -ForegroundColor Green
    } elseif ($response.StatusCode -eq 404) {
        Write-Host "❌ Dallas Arboretum endpoint NOT FOUND - API needs redeployment" -ForegroundColor Red
    } else {
        Write-Host "⚠️  Endpoint returned status: $($response.StatusCode)" -ForegroundColor Yellow
        Write-Host "   Response: $($response.Content)" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Error checking endpoint" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "💡 If endpoint is missing, manually redeploy API service in Railway dashboard" -ForegroundColor Cyan
