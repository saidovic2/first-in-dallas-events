# Simple Plugin Deployment Script
# Run this whenever you make changes to deploy to GitHub

param(
    [Parameter(Mandatory=$true)]
    [string]$Version,
    
    [Parameter(Mandatory=$true)]
    [string]$Message
)

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Deploying Events CMS Directory Plugin" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$pluginPath = "wordpress-plugin\events-cms-directory"

# Step 1: Update version in plugin file
Write-Host "Step 1: Updating version to $Version..." -ForegroundColor Yellow
$phpFile = "$pluginPath\events-cms-directory.php"
$content = Get-Content $phpFile -Raw
$content = $content -replace "(\* Version:\s+)[\d\.]+", "`$1$Version"
Set-Content $phpFile $content -NoNewline
Write-Host "  Version updated!" -ForegroundColor Green

# Step 2: Commit changes
Write-Host ""
Write-Host "Step 2: Committing changes..." -ForegroundColor Yellow
Push-Location $pluginPath
git add .
git commit -m "v$Version - $Message"
Write-Host "  Changes committed!" -ForegroundColor Green

# Step 3: Push to GitHub
Write-Host ""
Write-Host "Step 3: Pushing to GitHub..." -ForegroundColor Yellow
git push origin main
Write-Host "  Pushed to GitHub!" -ForegroundColor Green
Pop-Location

# Step 4: Instructions for release
Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "  SUCCESS! Almost done..." -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "FINAL STEP: Create GitHub Release" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Go to: https://github.com/saidovic2/events-cms-directory/releases/new" -ForegroundColor White
Write-Host "2. Tag: v$Version" -ForegroundColor White
Write-Host "3. Title: Version $Version" -ForegroundColor White
Write-Host "4. Description: $Message" -ForegroundColor White
Write-Host "5. Click 'Publish release'" -ForegroundColor White
Write-Host ""
Write-Host "After publishing, WordPress will auto-detect the update!" -ForegroundColor Cyan
Write-Host ""
