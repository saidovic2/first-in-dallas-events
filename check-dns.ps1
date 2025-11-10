# Check DNS propagation for hub.firstindallas.com
Write-Host "Checking DNS for hub.firstindallas.com..." -ForegroundColor Cyan
Write-Host ""

try {
    $result = nslookup hub.firstindallas.com 2>&1
    Write-Host $result
    Write-Host ""
    
    if ($result -match "cname.vercel-dns.com") {
        Write-Host "✅ DNS is configured correctly!" -ForegroundColor Green
        Write-Host "Your domain should work within a few minutes." -ForegroundColor Green
    } else {
        Write-Host "⏳ DNS not propagated yet. Wait a few minutes and try again." -ForegroundColor Yellow
    }
} catch {
    Write-Host "⏳ DNS not found yet. Wait a few minutes and try again." -ForegroundColor Yellow
}
