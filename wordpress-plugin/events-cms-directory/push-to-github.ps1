# Push Plugin to GitHub
# Run this script to commit and push changes

param(
    [string]$CommitMessage = "Update plugin"
)

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  Push Plugin to GitHub" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is initialized
if (-not (Test-Path ".git")) {
    Write-Host "Git not initialized. Run FIRST TIME SETUP:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "git init" -ForegroundColor White
    Write-Host "git config user.name 'saidovic2'" -ForegroundColor White
    Write-Host "git config user.email 'your-email@example.com'" -ForegroundColor White
    Write-Host "git remote add origin https://github.com/saidovic2/events-cms-directory.git" -ForegroundColor White
    Write-Host "git branch -M main" -ForegroundColor White
    Write-Host ""
    exit 1
}

# Add all changes
Write-Host "Adding files..." -ForegroundColor Yellow
git add .

# Show status
Write-Host ""
Write-Host "Changed files:" -ForegroundColor Cyan
git status --short

# Commit
Write-Host ""
Write-Host "Committing with message: $CommitMessage" -ForegroundColor Yellow
git commit -m $CommitMessage

# Push
Write-Host ""
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
git push origin main

Write-Host ""
Write-Host "SUCCESS! Changes pushed to GitHub" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Go to: https://github.com/saidovic2/events-cms-directory" -ForegroundColor White
Write-Host "2. Create a new release to trigger WordPress updates" -ForegroundColor White
Write-Host ""
