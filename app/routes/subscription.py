import os
import stripe
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..auth import get_current_user
from ..db import get_db
from ..models import User

stripe.api_key = os.getenv("STRIPE_API_KEY", "")

router = APIRouter()

class SubscribeRequest(BaseModel):
    price_id: str

@router.get("/pricing")
def pricing():
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe not configured")
    prices = stripe.Price.list(active=True, expand=["data.product"])
    plans = []
    for p in prices.data:
        name = p.product["name"] if isinstance(p.product, dict) else p.get("nickname")
        plans.append({
            "id": p.id,
            "name": name,
            "currency": p.currency,
            "amount": p.unit_amount,
        })
    return {"plans": plans}

@router.post("/subscribe")
def subscribe(data: SubscribeRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe not configured")
    if not user.stripe_customer_id:
        customer = stripe.Customer.create(email=user.email)
        user.stripe_customer_id = customer.id
    session = stripe.checkout.Session.create(
        customer=user.stripe_customer_id,
        line_items=[{"price": data.price_id, "quantity": 1}],
        mode="subscription",
        success_url=os.getenv("STRIPE_SUCCESS_URL", "http://localhost:3000/dashboard"),
        cancel_url=os.getenv("STRIPE_CANCEL_URL", "http://localhost:3000/pricing"),
    )
    user.subscription_status = "active"
    db.add(user)
    db.commit()
    return {"checkout_url": session.url}

@router.post("/cancel")
def cancel(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe not configured")
    if not user.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No Stripe customer")
    session = stripe.billing_portal.Session.create(
        customer=user.stripe_customer_id,
        return_url=os.getenv("STRIPE_RETURN_URL", "http://localhost:3000/dashboard"),
    )
    user.subscription_status = "inactive"
    db.add(user)
    db.commit()
    return {"url": session.url}
