from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.types import JSON
from datetime import datetime, timezone
from .db import Base
import enum

class ListingType(str, enum.Enum):
    RFQ = "RFQ"
    OFFER = "OFFER"

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    stripe_customer_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    subscription_status: Mapped[str] = mapped_column(String(20), default="inactive")

    listings: Mapped[list["Listing"]] = relationship("Listing", back_populates="owner")
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="sender")

class Listing(Base):
    __tablename__ = "listings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    type: Mapped[str] = mapped_column(Enum(ListingType), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(50), index=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    quantity: Mapped[str] = mapped_column(String(50), default="")
    incoterm: Mapped[str] = mapped_column(String(20), default="")
    country: Mapped[str] = mapped_column(String(80), default="")
    city: Mapped[str] = mapped_column(String(80), default="")
    status: Mapped[str] = mapped_column(String(20), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner: Mapped["User"] = relationship("User", back_populates="listings")
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="listing", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"), index=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    listing: Mapped["Listing"] = relationship("Listing", back_populates="messages")
    sender: Mapped["User"] = relationship("User", back_populates="messages")
