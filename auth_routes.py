from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.sql_models import User
from schemas import UserCreate, UserLogin, Token, UserResponse
from services.auth_service import AuthService
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = AuthService.get_password_hash(user.password)
    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    print(f"Login attempt for: {user_credentials.email}")
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    if not user:
        print(f"User not found: {user_credentials.email}")
    else:
        is_valid = AuthService.verify_password(user_credentials.password, user.hashed_password)
        print(f"User found: {user.email}, Role: {user.role}, Password Valid: {is_valid}")
        # print(f"Stored Hash: {user.hashed_password}") # Check hash if needed

    if not user or not AuthService.verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = AuthService.create_access_token(
        data={"sub": user.email, "role": user.role, "user_id": user.id}
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "role": user.role,
        "user_id": user.id,
        "name": user.name
    }

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = AuthService.decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    email = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def check_role(roles: list):
    def role_checker(user: User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return user
    return role_checker
