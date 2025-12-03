# Delete all Dallas Library events via API
$API_URL = "https://first-in-dallas-events-production.up.railway.app"

Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "🗑️  Deleting Dallas Library Events from Database" -ForegroundColor Cyan
Write-Host "================================================================================`n" -ForegroundColor Cyan

# Get all Dallas Library events
Write-Host "📊 Fetching Dallas Library events..." -ForegroundColor Yellow
$response = Invoke-RestMethod -Uri "$API_URL/api/events?source_type=DALLAS_LIBRARY&limit=1000" -Method Get

$events = $response
$count = $events.Count

if ($count -eq 0) {
    Write-Host "✅ No Dallas Library events found in database`n" -ForegroundColor Green
    exit 0
}

Write-Host "Found $count Dallas Library events`n" -ForegroundColor Yellow

# Show first 5
Write-Host "Sample events:" -ForegroundColor White
for ($i = 0; $i -lt [Math]::Min(5, $count); $i++) {
    Write-Host "   - $($events[$i].title) (ID: $($events[$i].id))" -ForegroundColor Gray
}

if ($count -gt 5) {
    Write-Host "   ... and $($count - 5) more`n" -ForegroundColor Gray
}

# Confirm deletion
Write-Host "`n⚠️  This will DELETE all $count Dallas Library events!" -ForegroundColor Red
$confirm = Read-Host "Type 'DELETE' to confirm"

if ($confirm -ne "DELETE") {
    Write-Host "`n❌ Deletion cancelled`n" -ForegroundColor Yellow
    exit 0
}

# Delete each event
Write-Host "`n🗑️  Deleting events..." -ForegroundColor Yellow
$deleted = 0

foreach ($event in $events) {
    try {
        Invoke-RestMethod -Uri "$API_URL/api/events/$($event.id)" -Method Delete
        $deleted++
        Write-Host "   ✓ Deleted: $($event.title)" -ForegroundColor Green
    } catch {
        Write-Host "   ✗ Failed to delete ID $($event.id): $_" -ForegroundColor Red
    }
}

Write-Host "`n✅ Successfully deleted $deleted out of $count Dallas Library events!" -ForegroundColor Green
Write-Host "🎉 Database is clean - ready for fresh sync`n" -ForegroundColor Cyan
