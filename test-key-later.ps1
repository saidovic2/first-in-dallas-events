# Test Ticketmaster Key After Waiting
Write-Host "⏰ Waiting 2 minutes for key to activate..." -ForegroundColor Yellow
Start-Sleep -Seconds 120

Write-Host "`n🧪 Testing key now..." -ForegroundColor Cyan
python test-ticketmaster-key.py

Write-Host "`n💡 If still failing, you need to:" -ForegroundColor Yellow
Write-Host "  1. Create new app from Discovery API page" -ForegroundColor White
Write-Host "  2. Or contact Ticketmaster support" -ForegroundColor White
