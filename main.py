
import os
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from db import init_db
from models import Commodity, User
from schemas import TokenResponse, CommodityIn, CommodityOut, RegisterRequest
from auth import authenticate, create_access_token, get_current_user, admin_required, get_db
from passlib.hash import bcrypt

VERSION = "v0.2.2"

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

# ---------- AUTH ----------
@app.post("/auth/register")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    u = User(email=body.email, password_hash=bcrypt.hash(body.password), is_admin=False)
    db.add(u); db.commit(); return {"ok": True}

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

# ---------- USERS (ADMIN) ----------
@app.get("/users")
def list_users(_: User = Depends(admin_required), db: Session = Depends(get_db)):
    users = db.query(User).all()
    # never return plaintext passwords
    return [{"id": u.id, "email": u.email, "is_admin": u.is_admin, "password_hash": getattr(u, "password_hash", None)} for u in users]

# ---------- SUBSCRIPTIONS (placeholder) ----------
@app.get("/stats/subscriptions")
def sub_stats(_: User = Depends(admin_required)):
    # placeholder numbers; Stripe wiring next
    active = 7
    mrr_usd = 7 * 499
    arpu_usd = 499
    return {"active": active, "mrr_usd": mrr_usd, "arpu_usd": arpu_usd}

# ---------- SUPPLY CHAIN ALERTS (placeholder) ----------
@app.get("/alerts/supplychain")
def supplychain_alerts(_: User = Depends(admin_required)):
    alerts = [
        {"headline": "Urgent wheat demand in Georgia", "detail": "Importers in Poti seeking 3,000 MT within 10 days; CIF rising due to port congestion."},
        {"headline": "Container delays at Mersin", "detail": "Average dwell time +18%; consider rail via Kars-Tbilisi-Baku corridor."},
    ]
    return {"alerts": alerts}

# ---------- COMMODITIES ----------
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

# ---------- AI ADD (placeholder) ----------
@app.post("/commodities/ai-add")
def ai_add(data: dict, user: User = Depends(admin_required)):
    prompt = data.get("prompt", "")
    # placeholder output until AI integration
    items = [
        {"name": "Wheat (HRW)", "unit": "$/ton", "price": 252, "source": "ai"},
        {"name": "Corn", "unit": "$/ton", "price": 198, "source": "ai"},
        {"name": "Sunflower oil", "unit": "$/ton", "price": 910, "source": "ai"},
    ]
    return {"prompt": prompt, "items": items}
