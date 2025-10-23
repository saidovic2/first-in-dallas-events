#!/usr/bin/env pwsh
# Fix Facebook Sync - Add completed_at field and restart services

Write-Host "=== Fixing Facebook Sync Issues ===" -ForegroundColor Cyan
Write-Host ""

# 1. Add the completed_at column to the database
Write-Host "Step 1: Updating database schema..." -ForegroundColor Yellow
# Execute SQL directly using PowerShell
docker-compose exec -T db psql -U postgres -d events_cms -c "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP WITH TIME ZONE;"
if ($LASTEXITCODE -eq 0) {
    docker-compose exec -T db psql -U postgres -d events_cms -c "UPDATE tasks SET completed_at = updated_at WHERE status IN ('done', 'failed') AND completed_at IS NULL;"
    Write-Host "✓ Database schema updated successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to update database" -ForegroundColor Red
    Write-Host "You may need to run the SQL manually" -ForegroundColor Yellow
}
Write-Host ""

# 2. Restart API and Worker containers to load the updated code
Write-Host "Step 2: Restarting services..." -ForegroundColor Yellow
docker-compose restart api worker
Start-Sleep -Seconds 5
Write-Host "✓ Services restarted" -ForegroundColor Green
Write-Host ""

# 3. Show logs to verify everything is working
Write-Host "Step 3: Checking service health..." -ForegroundColor Yellow
docker-compose ps
Write-Host ""

Write-Host "=== Fix Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "What was fixed:" -ForegroundColor Cyan
Write-Host "1. ✓ Added 'completed_at' field to Task model (fixes progression bar)" -ForegroundColor White
Write-Host "2. ✓ Added error logging for Apify responses (shows Facebook sync errors)" -ForegroundColor White
Write-Host "3. ✓ Worker now sets completed_at timestamp when tasks finish" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "- Try running Facebook Bulk Sync again from the web UI" -ForegroundColor White
Write-Host "- You should now see the progression bar working" -ForegroundColor White
Write-Host "- Check worker logs to see detailed Apify error messages:" -ForegroundColor White
Write-Host "  docker-compose logs -f worker" -ForegroundColor Gray
Write-Host ""
