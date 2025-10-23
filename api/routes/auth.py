from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user import LoginRequest, TokenResponse, UserResponse
from utils.auth import verify_password, create_access_token, get_current_user, get_password_hash

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
    
    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)

@router.post("/create-admin")
async def create_admin_user(db: Session = Depends(get_db)):
    """
    Temporary endpoint to create admin user in production.
    Remove this after creating your admin!
    """
    # Check if admin already exists
    existing_admin = db.query(User).filter(User.email == "admin@firstindallas.com").first()
    if existing_admin:
        return {"message": "Admin user already exists", "email": "admin@firstindallas.com"}
    
    # Create admin user
    admin = User(
        email="admin@firstindallas.com",
        name="Admin",
        password_hash=get_password_hash("admin123")
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    return {
        "message": "Admin user created successfully!",
        "email": "admin@firstindallas.com",
        "password": "admin123",
        "note": "Please change this password after first login!"
    }
