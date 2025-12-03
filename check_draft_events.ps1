$base_url = "https://wonderful-vibrancy-production.up.railway.app/api/events"

Write-Host "`n🔍 Checking event status distribution..." -ForegroundColor Cyan
Write-Host ""

# Get DRAFT events
try {
    $draft_url = $base_url + "?limit=300"
    $all_events = Invoke-RestMethod -Uri $draft_url
    
    $draft_count = ($all_events | Where-Object { $_.status -eq "DRAFT" }).Count
    $published_count = ($all_events | Where-Object { $_.status -eq "PUBLISHED" }).Count
    
    Write-Host "📊 Event Status Summary:" -ForegroundColor Yellow
    Write-Host "  - DRAFT: $draft_count" -ForegroundColor Yellow
    Write-Host "  - PUBLISHED: $published_count" -ForegroundColor Green
    Write-Host "  - TOTAL: $($all_events.Count)" -ForegroundColor Cyan
    Write-Host ""
    
    if ($draft_count -gt 0) {
        Write-Host "✅ You have DRAFT events ready to review!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  No DRAFT events found. Run the SQL update command in Railway." -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Error checking events: $_" -ForegroundColor Red
}
