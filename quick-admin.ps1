# Quick Admin User Creation
Write-Host "Creating admin user in database..." -ForegroundColor Yellow
Write-Host ""

# Create admin user using Python in container
$pythonCode = @'
import sys
sys.path.insert(0, "/app")
from database import SessionLocal
from models.user import User
import bcrypt

db = SessionLocal()
try:
    admin = db.query(User).filter(User.email == "admin@example.com").first()
    if admin:
        db.delete(admin)
        db.commit()
        print("Removed existing admin")
    
    # Hash password directly with bcrypt
    password_bytes = "admin123".encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    admin = User(
        name="Admin User",
        email="admin@example.com",
        password_hash=hashed.decode('utf-8'),
        role="admin"
    )
    db.add(admin)
    db.commit()
    print("✓ Admin user created!")
    print("Email: admin@example.com")
    print("Password: admin123")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
'@

# Execute in API container
$pythonCode | docker-compose exec -T api python

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Admin User Ready!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Login at: http://localhost:3001" -ForegroundColor Cyan
Write-Host "Email: admin@example.com" -ForegroundColor White
Write-Host "Password: admin123" -ForegroundColor White
Write-Host ""
