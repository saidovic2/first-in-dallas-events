# Check events via API
$base_url = "https://wonderful-vibrancy-production.up.railway.app/api/events"

Write-Host "`n🔍 Checking PUBLISHED events..." -ForegroundColor Cyan
$published = Invoke-RestMethod -Uri ($base_url + "?status=PUBLISHED" + "&limit=200")
Write-Host "✅ PUBLISHED events: $($published.Count)" -ForegroundColor Green

Write-Host "`n🔍 Checking DRAFT events..." -ForegroundColor Cyan
$draft = Invoke-RestMethod -Uri ($base_url + "?status=DRAFT" + "&limit=200")
Write-Host "✅ DRAFT events: $($draft.Count)" -ForegroundColor Yellow

Write-Host "`n🔍 Checking ALL events..." -ForegroundColor Cyan
$all = Invoke-RestMethod -Uri ($base_url + "?limit=200")
Write-Host "✅ TOTAL events: $($all.Count)" -ForegroundColor Blue

Write-Host "`n📊 Summary:" -ForegroundColor Magenta
Write-Host "  - Total: $($all.Count)"
Write-Host "  - Published: $($published.Count)"
Write-Host "  - Draft: $($draft.Count)"

if ($published.Count -gt 0) {
    Write-Host "`n📝 Sample published events:" -ForegroundColor Green
    $published | Select-Object -First 3 | ForEach-Object {
        Write-Host "  - $($_.title)"
    }
}

if ($draft.Count -gt 0) {
    Write-Host "`n📝 Sample draft events:" -ForegroundColor Yellow
    $draft | Select-Object -First 3 | ForEach-Object {
        Write-Host "  - $($_.title)"
    }
}
