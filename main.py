import os
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from db import init_db
from models import Commodity, User
from schemas import TokenResponse, CommodityIn, CommodityOut
from auth import authenticate, create_access_token, get_current_user, admin_required, get_db

VERSION = "v0.2.1"

app = FastAPI(title="FalconTrade API", version=VERSION)

origins = os.getenv("CORS_ORIGINS", "https://falcontrade.org,https://www.falcontrade.org,https://falcontrade-frontend.vercel.app,https://falcontrade.vercel.app").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_start():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/version")
def version():
    return {"name": "FalconTrade API", "version": VERSION, "deployed_at": datetime.now(timezone.utc).isoformat()}

@app.post("/auth/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(user.email)
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"email": user.email, "is_admin": user.is_admin}

@app.get("/commodities", response_model=List[CommodityOut])
def list_commodities(db: Session = Depends(get_db)):
    items = db.query(Commodity).order_by(Commodity.name).all()
    return items

@app.post("/commodities", response_model=CommodityOut)
def create_commodity(data: CommodityIn, user: User = Depends(admin_required), db: Session = Depends(get_db)):
    exists = db.query(Commodity).filter(Commodity.name.ilike(data.name)).first()
    if exists:
        raise HTTPException(status_code=409, detail="Commodity already exists")
    c = Commodity(name=data.name, unit=data.unit, price=data.price, source=data.source)
    db.add(c); db.commit(); db.refresh(c)
    return c

@app.put("/commodities/{cid}", response_model=CommodityOut)
def update_commodity(cid: int, data: CommodityIn, user: User = Depends(admin_required), db: Session = Depends(get_db)):
    c = db.query(Commodity).get(cid)
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    c.name = data.name; c.unit = data.unit; c.price = data.price; c.source = data.source
    db.commit(); db.refresh(c)
    return c

@app.delete("/commodities/{cid}")
def delete_commodity(cid: int, user: User = Depends(admin_required), db: Session = Depends(get_db)):
    c = db.query(Commodity).get(cid)
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(c); db.commit()
    return {"ok": True}