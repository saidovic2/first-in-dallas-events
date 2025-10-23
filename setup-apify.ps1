# Apify Setup Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Apify Facebook Scraper Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (Test-Path ".env") {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
    Write-Host ""
    Write-Host "Current content:" -ForegroundColor Yellow
    Get-Content ".env"
    Write-Host ""
    $overwrite = Read-Host "Do you want to add/update the Apify token? (y/n)"
    if ($overwrite -ne "y") {
        Write-Host "Cancelled" -ForegroundColor Yellow
        exit 0
    }
} else {
    Write-Host "Creating new .env file..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Get Your Apify API Token" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Go to: https://console.apify.com/account/integrations" -ForegroundColor White
Write-Host "2. Copy your API token" -ForegroundColor White
Write-Host "3. Paste it below" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Your token will be stored locally and kept private" -ForegroundColor Yellow
Write-Host ""

$token = Read-Host "Enter your Apify API token (or press Enter to skip)"

if ([string]::IsNullOrWhiteSpace($token)) {
    Write-Host ""
    Write-Host "⚠️  No token provided. Facebook scraping will use basic method." -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "✓ Token received!" -ForegroundColor Green
    
    # Create or update .env file
    $envContent = @"
# Apify API Token for Facebook Scraping
APIFY_API_TOKEN=$token

# WordPress Integration (optional)
WP_BASE_URL=
WP_USER=
WP_APP_PASSWORD=
"@
    
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "✓ .env file created/updated" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Restarting Worker" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

docker-compose restart worker

Write-Host ""
Write-Host "✓ Worker restarted!" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Go to http://localhost:3001/add" -ForegroundColor White
Write-Host "  2. Paste a Facebook event URL" -ForegroundColor White
Write-Host "  3. Click 'Extract Events'" -ForegroundColor White
Write-Host ""
Write-Host "Monitor extraction:" -ForegroundColor Yellow
Write-Host "  docker-compose logs -f worker" -ForegroundColor White
Write-Host ""
Write-Host "Read full guide:" -ForegroundColor Yellow
Write-Host "  APIFY_SETUP.md" -ForegroundColor White
Write-Host ""
