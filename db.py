import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Commodity
from passlib.hash import bcrypt

DB_URL = os.getenv("DATABASE_URL", "sqlite:///./falcontrade.db")
connect_args = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}
engine = create_engine(DB_URL, echo=False, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        admin_email = os.getenv("ADMIN_EMAIL", "admin@falcontrade.org")
        admin_pwd = os.getenv("ADMIN_PASSWORD", "admin123")
        exists = db.query(User).filter(User.email == admin_email).first()
        if not exists:
            from models import User, Commodity
            u = User(email=admin_email, password_hash=bcrypt.hash(admin_pwd), is_admin=True)
            db.add(u)
            # seed commodities
            samples = [
                Commodity(name="Wheat", unit="$/ton", price=250.0, source="seed"),
                Commodity(name="Barley", unit="$/ton", price=220.0, source="seed"),
                Commodity(name="Sunflower Oil", unit="$/ton", price=980.0, source="seed"),
                Commodity(name="Sugar", unit="$/ton", price=570.0, source="seed"),
                Commodity(name="Steel", unit="$/ton", price=600.0, source="seed"),
            ]
            for s in samples: db.add(s)
            db.commit()