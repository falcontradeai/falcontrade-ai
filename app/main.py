import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import Base, engine
from .routes import auth as auth_routes
from .routes import misc as misc_routes
from .routes import listings as listings_routes

app = FastAPI(title="FalconTrade API", version="v1.0")

origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,https://falcontrade.org,https://www.falcontrade.org,https://falcontrade-frontend.vercel.app,https://falcontrade.vercel.app").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

if os.getenv("SEED_SAMPLE", "1") == "1":
    try:
        from .seed import run as seed_run
        seed_run()
    except Exception as e:
        print("Seed error:", e)

app.include_router(misc_routes.router)
app.include_router(auth_routes.router)
app.include_router(listings_routes.router)
