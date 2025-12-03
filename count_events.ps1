$uri = "https://wonderful-vibrancy-production.up.railway.app/api/events?limit=200"
$response = Invoke-RestMethod -Uri $uri
Write-Host "Total events in database: $($response.Count)"
Write-Host ""
Write-Host "First 5 events:"
$response | Select-Object -First 5 | ForEach-Object {
    Write-Host "  ID: $($_.id) - $($_.title.Substring(0, [Math]::Min(50, $_.title.Length)))... - Status: $($_.status)"
}
