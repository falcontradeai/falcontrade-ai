import os
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.hash import bcrypt
from sqlalchemy.orm import Session

from models import User
from db import SessionLocal

SECRET_KEY = os.getenv("JWT_SECRET", "supersecret")
ALGO = "HS256"
ACCESS_MIN = int(os.getenv("ACCESS_TOKEN_MIN", "120"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def authenticate(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not bcrypt.verify(password, user.password_hash):
        return None
    return user

def create_access_token(sub: str):
    now = datetime.now(timezone.utc)
    payload = {"sub": sub, "iat": int(now.timestamp()), "exp": int((now + timedelta(minutes=ACCESS_MIN)).timestamp())}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGO)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    cred_exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGO])
        email = payload.get("sub")
        if email is None:
            raise cred_exc
    except JWTError:
        raise cred_exc
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise cred_exc
    return user

def admin_required(user: User = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return user