# Setup Event Organizer Hub
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "First in Dallas - Event Organizer Hub" -ForegroundColor Cyan
Write-Host "Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if hub folder exists
if (-not (Test-Path ".\hub")) {
    Write-Host "ERROR: Hub folder not found!" -ForegroundColor Red
    exit 1
}

Write-Host "Step 1: Installing dependencies..." -ForegroundColor Yellow
cd hub

# Install dependencies
npm install

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✓ Dependencies installed successfully!" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Set up Supabase account (see HUB_SETUP_COMPLETE.md)" -ForegroundColor White
Write-Host "2. Create .env.local with your Supabase credentials" -ForegroundColor White
Write-Host "3. Run: cd hub && npm run dev" -ForegroundColor White
Write-Host "4. Open: http://localhost:3001" -ForegroundColor White
Write-Host ""

Write-Host "Full documentation: HUB_SETUP_COMPLETE.md" -ForegroundColor Yellow
