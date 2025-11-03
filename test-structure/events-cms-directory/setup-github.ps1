# First Time GitHub Setup
# Run this once to initialize Git and push to GitHub

param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubEmail
)

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  First Time GitHub Setup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if already initialized
if (Test-Path ".git") {
    Write-Host "WARNING: Git already initialized!" -ForegroundColor Yellow
    Write-Host "If you want to re-initialize, delete .git folder first" -ForegroundColor Yellow
    Write-Host ""
    $response = Read-Host "Continue anyway? (y/n)"
    if ($response -ne "y") {
        exit 0
    }
}

Write-Host "Step 1: Initialize Git" -ForegroundColor Yellow
git init

Write-Host ""
Write-Host "Step 2: Configure Git" -ForegroundColor Yellow
git config user.name "saidovic2"
git config user.email $GitHubEmail
Write-Host "  Username: saidovic2" -ForegroundColor White
Write-Host "  Email: $GitHubEmail" -ForegroundColor White

Write-Host ""
Write-Host "Step 3: Add files" -ForegroundColor Yellow
git add .
Write-Host "  All files added" -ForegroundColor White

Write-Host ""
Write-Host "Step 4: Initial commit" -ForegroundColor Yellow
git commit -m "Initial commit - Events CMS Directory Plugin v1.1.0"

Write-Host ""
Write-Host "Step 5: Add GitHub remote" -ForegroundColor Yellow
# Check if remote already exists
$remoteExists = git remote | Select-String "origin"
if ($remoteExists) {
    Write-Host "  Remote 'origin' already exists, using it" -ForegroundColor White
} else {
    git remote add origin https://github.com/saidovic2/events-cms-directory.git
    Write-Host "  Remote added: https://github.com/saidovic2/events-cms-directory.git" -ForegroundColor White
}

Write-Host ""
Write-Host "Step 6: Set main branch" -ForegroundColor Yellow
git branch -M main

Write-Host ""
Write-Host "Step 7: Push to GitHub" -ForegroundColor Yellow
Write-Host "  You may be asked to log in to GitHub..." -ForegroundColor Cyan
Write-Host ""

git push -u origin main

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  SUCCESS! Plugin pushed to GitHub!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Visit: https://github.com/saidovic2/events-cms-directory" -ForegroundColor White
Write-Host "2. Go to Releases -> Create a new release" -ForegroundColor White
Write-Host "3. Tag: v1.1.0" -ForegroundColor White
Write-Host "4. Publish release" -ForegroundColor White
Write-Host "5. Download the ZIP and upload to WordPress" -ForegroundColor White
Write-Host ""
Write-Host "For future updates, use: .\push-to-github.ps1 'Your commit message'" -ForegroundColor Cyan
Write-Host ""
