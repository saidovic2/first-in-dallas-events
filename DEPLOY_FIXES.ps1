#!/usr/bin/env pwsh
# Deploy All Fixes to Railway

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Events CMS - Deploy Fixes Script    " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is available
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Git is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Git first: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

Write-Host "📋 Summary of Changes:" -ForegroundColor Green
Write-Host "  ✅ Created railway.toml files for proper deployment" -ForegroundColor White
Write-Host "  ✅ Fixed Dockerfiles for Railway compatibility" -ForegroundColor White
Write-Host "  ✅ Changed event status from DRAFT to PUBLISHED" -ForegroundColor White
Write-Host "  ✅ Updated worker to auto-publish synced events" -ForegroundColor White
Write-Host ""

# Check if there are changes to commit
$status = git status --porcelain
if (-not $status) {
    Write-Host "⚠️  No changes to commit" -ForegroundColor Yellow
    Write-Host "All fixes may already be deployed" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To redeploy anyway, run:" -ForegroundColor Cyan
    Write-Host "  git commit --allow-empty -m 'Trigger redeploy'" -ForegroundColor White
    Write-Host "  git push" -ForegroundColor White
    exit 0
}

Write-Host "📦 Staging changes..." -ForegroundColor Cyan
git add .

Write-Host ""
Write-Host "💾 Committing changes..." -ForegroundColor Cyan
git commit -m "Fix Railway deployment and event status issues

- Add railway.toml configuration for API, Worker, and Web services
- Update Dockerfiles for Railway PORT variable
- Change event status from DRAFT to PUBLISHED
- Ensure synced events appear on WordPress immediately
"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to commit changes" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🚀 Pushing to GitHub (will trigger Railway deployment)..." -ForegroundColor Cyan
git push

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to push to GitHub" -ForegroundColor Red
    Write-Host ""
    Write-Host "If this is your first push, you may need to set upstream:" -ForegroundColor Yellow
    Write-Host "  git push -u origin main" -ForegroundColor White
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   ✅ Successfully Pushed to GitHub!    " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "📊 Next Steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1️⃣  Go to Railway Dashboard:" -ForegroundColor Yellow
Write-Host "   https://railway.app/dashboard" -ForegroundColor White
Write-Host ""
Write-Host "2️⃣  Monitor your deployments:" -ForegroundColor Yellow
Write-Host "   • first-in-dallas-events (API)" -ForegroundColor White
Write-Host "   • wonderful-vibrancy (Worker)" -ForegroundColor White
Write-Host "   Wait for both to show 'Active' status" -ForegroundColor White
Write-Host ""
Write-Host "3️⃣  Update existing events in database:" -ForegroundColor Yellow
Write-Host "   Run FIX_EVENT_STATUS.sql in Railway PostgreSQL" -ForegroundColor White
Write-Host "   (Railway → PostgreSQL → Query tab)" -ForegroundColor White
Write-Host ""
Write-Host "4️⃣  Update WordPress settings:" -ForegroundColor Yellow
Write-Host "   Settings → Events CMS → Update API URL" -ForegroundColor White
Write-Host "   Use your Railway API domain" -ForegroundColor White
Write-Host ""
Write-Host "5️⃣  Test the sync:" -ForegroundColor Yellow
Write-Host "   CMS Dashboard → Sync → Click 'Sync Eventbrite'" -ForegroundColor White
Write-Host ""
Write-Host "6️⃣  Check WordPress:" -ForegroundColor Yellow
Write-Host "   Visit your Events page - events should appear!" -ForegroundColor White
Write-Host ""

Write-Host "📖 For detailed instructions, see:" -ForegroundColor Cyan
Write-Host "   COMPLETE_FIX_GUIDE.md" -ForegroundColor White
Write-Host ""

Write-Host "🎉 Deployment initiated successfully!" -ForegroundColor Green
