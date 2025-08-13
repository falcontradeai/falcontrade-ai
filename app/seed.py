import os
from sqlalchemy.orm import Session
from .db import SessionLocal, Base, engine
from .models import User, Listing, ListingType
from .auth import hash_password

def run():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        admin_email = os.getenv("ADMIN_EMAIL", "admin@falcontrade.org")
        admin_pass = os.getenv("ADMIN_PASSWORD", "Admin123!")
        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            admin = User(email=admin_email, hashed_password=hash_password(admin_pass), is_admin=True)
            db.add(admin); db.commit(); db.refresh(admin)

        user_email = "demo@falcontrade.org"
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            user = User(email=user_email, hashed_password=hash_password("Demo123!"), is_admin=False)
            db.add(user); db.commit(); db.refresh(user)

        def add_listing(type_, category, title, country, details, qty="100 MT", incoterm="CIF", city=""):
            l = Listing(type=ListingType(type_), category=category, title=title, details=details,
                        quantity=qty, incoterm=incoterm, country=country, city=city, status="published", owner_id=user.id)
            db.add(l)

        items = [
            ("RFQ","grain","Wheat grade A, 12.5% protein","Azerbaijan", {"protein":"12.5%","moisture":"12%","pack":"bulk"}),
            ("OFFER","grain","Corn feed grade, 50k MT monthly","Kazakhstan", {"moisture":"14%","pack":"bulk"}),
            ("RFQ","oils","Sunflower oil, refined, IBC","Azerbaijan", {"FFA":"<=0.1%","pack":"IBC 1000L"}),
            ("OFFER","oils","Palm olein CP10, drums","UAE", {"iodine":"56-60","pack":"200L drums"}),
            ("RFQ","fertilizer","Urea 46% N, granular","Turkey", {"nitrogen":"46%","pack":"50kg bags"}),
            ("OFFER","fertilizer","NPK 15-15-15","UAE", {"npk":"15-15-15","pack":"bulk/50kg"}),
            ("RFQ","textiles","Cotton fabric 200 GSM, white","Azerbaijan", {"gsm":200,"composition":"100% cotton","width":"150cm"}),
            ("OFFER","textiles","Silk fabric, 80 GSM dyed","China", {"gsm":80,"composition":"100% silk","finish":"dyed"}),
            ("RFQ","panels","Sandwich panels, 50mm PIR","Georgia", {"thickness":"50mm","rating":"PIR","color":"ral9002"}),
            ("OFFER","poultry","Fresh eggs, size M, halal","Turkey", {"grade":"M","pack":"30-tray carton","halal":True}),
        ]
        for it in items:
            add_listing(*it)

        db.commit()
        print("Seeded admin, demo user, and 10 listings.")
    finally:
        db.close()

if __name__ == "__main__":
    run()
