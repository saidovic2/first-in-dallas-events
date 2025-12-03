# Add dallas_arboretum to sourcetype enum via Railway CLI

Write-Host "🚀 Adding 'dallas_arboretum' to sourcetype enum on Railway..." -ForegroundColor Cyan

# Execute SQL via Railway CLI
$sql = "ALTER TYPE sourcetype ADD VALUE IF NOT EXISTS 'dallas_arboretum';"

Write-Host "📝 Executing SQL: $sql" -ForegroundColor Yellow

railway run --service Postgres psql -c $sql

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Successfully added 'dallas_arboretum' to sourcetype enum!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎉 You can now run the Dallas Arboretum sync from the CMS dashboard!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Command completed (may already exist)" -ForegroundColor Yellow
}

# Verify the change
Write-Host ""
Write-Host "📋 Verifying enum values..." -ForegroundColor Cyan
railway run --service Postgres psql -c "SELECT unnest(enum_range(NULL::sourcetype));"
