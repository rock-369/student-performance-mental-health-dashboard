from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-this")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 hours

class AuthService:
    @staticmethod
    def verify_password(plain_password, hashed_password):
        if not hashed_password:
            return False
        # bcrypt needs bytes
        password_bytes = plain_password.encode('utf-8')
        if isinstance(hashed_password, str):
            hashed_bytes = hashed_password.encode('utf-8')
        else:
            hashed_bytes = hashed_password
            
        try:
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception:
            return False

    @staticmethod
    def get_password_hash(password):
        # bcrypt needs bytes
        password_bytes = password.encode('utf-8')
        # Generate salt and hash
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        # Store as string in DB
        return hashed.decode('utf-8')

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None
