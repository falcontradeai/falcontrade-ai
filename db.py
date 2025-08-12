from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User  # ✅ Added User model import

from passlib.context import CryptContext
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")

    # ✅ Check if admin user exists
    exists = db.query(User).filter(User.email == admin_email).first()
    if not exists:
        hashed_password = pwd_context.hash(admin_password)
        admin_user = User(email=admin_email, hashed_password=hashed_password, is_admin=True)
        db.add(admin_user)
        db.commit()
    db.close()
