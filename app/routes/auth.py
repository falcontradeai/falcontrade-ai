from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from ..db import get_db
from ..models import User, RevokedToken
from ..schemas import RegisterRequest, TokenResponse, MeResponse
from ..auth import hash_password, authenticate, create_access_token, get_current_user, oauth2_scheme
from email_validator import validate_email, EmailNotValidError

router = APIRouter()

@router.post("/auth/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    try:
        validate_email(data.email)
    except EmailNotValidError:
        raise HTTPException(status_code=400, detail="Invalid email")
    exists = db.query(User).filter(User.email == data.email).first()
    if exists:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(email=data.email, hashed_password=hash_password(data.password), is_admin=False)
    db.add(user); db.commit(); db.refresh(user)
    return {"ok": True}

@router.post("/auth/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate(db, form.username, form.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(user.email)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/auth/logout")
def logout(
    user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    if not db.query(RevokedToken).filter(RevokedToken.token == token).first():
        db.add(RevokedToken(token=token))
        db.commit()
    return {"ok": True}

@router.get("/me", response_model=MeResponse)
def me(user: User = Depends(get_current_user)):
    return {"email": user.email, "is_admin": user.is_admin}
