# Create Admin User Directly
Write-Host "Creating admin user..." -ForegroundColor Yellow

$createUserScript = @"
from database import SessionLocal
from models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

db = SessionLocal()
try:
    # Check if admin exists
    admin = db.query(User).filter(User.email == 'admin@example.com').first()
    if admin:
        print('Admin user already exists')
    else:
        # Create admin with simple password
        admin = User(
            name='Admin User',
            email='admin@example.com',
            password_hash=pwd_context.hash('admin123'),
            role='admin'
        )
        db.add(admin)
        db.commit()
        print('✓ Admin user created successfully')
        print('Email: admin@example.com')
        print('Password: admin123')
except Exception as e:
    print(f'Error: {e}')
    db.rollback()
finally:
    db.close()
"@

# Write script to temp file
$createUserScript | Out-File -FilePath ".\api\create_admin_temp.py" -Encoding UTF8

# Run it in container
docker-compose exec -T api python create_admin_temp.py

# Clean up
Remove-Item ".\api\create_admin_temp.py" -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "Done! Try logging in at http://localhost:3001" -ForegroundColor Green
Write-Host "Email: admin@example.com" -ForegroundColor White
Write-Host "Password: admin123" -ForegroundColor White
