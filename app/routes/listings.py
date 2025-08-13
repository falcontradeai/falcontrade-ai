from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import os, shutil
from ..db import get_db
from ..models import Listing, ListingType, User, Message
from ..schemas import ListingIn, ListingOut, MessageIn, MessageOut
from ..auth import get_current_user, admin_required

router = APIRouter()

def to_out(l: Listing) -> ListingOut:
    return ListingOut(
        id=l.id,
        type=l.type.value if hasattr(l.type, "value") else l.type,
        category=l.category, title=l.title,
        details=l.details or {}, quantity=l.quantity or "",
        incoterm=l.incoterm or "", country=l.country or "", city=l.city or "",
        status=l.status, created_at=l.created_at,
        owner_email=l.owner.email if l.owner else "unknown"
    )

@router.post("/listings", response_model=ListingOut)
def create_listing(data: ListingIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if data.type not in ("RFQ","OFFER"):
        raise HTTPException(status_code=400, detail="type must be RFQ or OFFER")
    l = Listing(
        type=ListingType(data.type), category=data.category, title=data.title,
        details=data.details or {}, quantity=data.quantity or "",
        incoterm=data.incoterm or "", country=data.country or "",
        city=data.city or "", status="draft", owner_id=user.id
    )
    db.add(l); db.commit(); db.refresh(l)
    return to_out(l)

@router.get("/market", response_model=List[ListingOut])
def market(
    type: Optional[str] = None,
    category: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = 200,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(Listing).filter(Listing.status == "published")
    if type in ("RFQ", "OFFER"):
        query = query.filter(Listing.type == ListingType(type))
    if category:
        query = query.filter(Listing.category == category)
    if q:
        like = f"%{q}%"
        from sqlalchemy import or_, cast, String
        query = query.filter(
            or_(
                Listing.title.ilike(like),
                cast(Listing.details, String).ilike(like),
                Listing.category.ilike(like),
            )
        )
    rows = (
        query.order_by(Listing.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [to_out(l) for l in rows]

@router.get("/listings/{lid}", response_model=ListingOut)
def get_listing(lid: int, db: Session = Depends(get_db)):
    l = db.query(Listing).get(lid)
    if not l or l.status != "published":
        raise HTTPException(status_code=404, detail="Not found")
    return to_out(l)

@router.post("/admin/listings/{lid}/publish")
def publish_listing(lid: int, admin: User = Depends(admin_required), db: Session = Depends(get_db)):
    l = db.query(Listing).get(lid)
    if not l:
        raise HTTPException(status_code=404, detail="Not found")
    l.status = "published"
    db.commit()
    return {"ok": True}

@router.post("/listings/{lid}/messages", response_model=MessageOut)
def add_message(lid: int, data: MessageIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    l = db.query(Listing).get(lid)
    if not l:
        raise HTTPException(status_code=404, detail="Not found")
    m = Message(body=data.body, listing_id=lid, sender_id=user.id)
    db.add(m); db.commit(); db.refresh(m)
    return MessageOut(id=m.id, body=m.body, created_at=m.created_at, sender_email=m.sender.email)

@router.get("/listings/{lid}/messages", response_model=List[MessageOut])
def list_messages(lid: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    l = db.query(Listing).get(lid)
    if not l:
        raise HTTPException(status_code=404, detail="Not found")
    rows = db.query(Message).filter(Message.listing_id == lid).order_by(Message.created_at.asc()).all()
    return [MessageOut(id=m.id, body=m.body, created_at=m.created_at, sender_email=m.sender.email) for m in rows]

@router.post("/listings/{lid}/attachments")
def upload_attachment(lid: int, file: UploadFile = File(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    l = db.query(Listing).get(lid)
    if not l:
        raise HTTPException(status_code=404, detail="Not found")
    os.makedirs("uploads", exist_ok=True)
    dest = os.path.join("uploads", f"{lid}_{file.filename}")
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"ok": True, "path": dest}
