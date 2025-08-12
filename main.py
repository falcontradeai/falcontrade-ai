from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
import os

app = FastAPI(title="FalconTrade API", version="0.2.1")

ALLOWED = ["https://falcontrade.org", "https://www.falcontrade.org"]
extra = [s.strip() for s in os.getenv("ALLOWED_ORIGINS","").split(",") if s.strip()]
allowed = ALLOWED + extra

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed if allowed else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PRICES = [
    {"name":"Wheat","unit":"$/ton","price":250.0,"source":"Preview"},
    {"name":"Barley","unit":"$/ton","price":220.0,"source":"Preview"},
    {"name":"Sunflower Oil","unit":"$/ton","price":980.0,"source":"Preview"},
    {"name":"Sugar","unit":"$/ton","price":570.0,"source":"Preview"},
    {"name":"Steel","unit":"$/ton","price":600.0,"source":"Preview"},
]

def now(): return datetime.now(timezone.utc).isoformat(timespec="seconds")

@app.get("/health")
def health(): return {"ok":True,"ts":now(),"version":"0.2.1"}

@app.get("/prices")
def prices(): return JSONResponse({"generated_at":now(),"base_currency":"USD","prices":PRICES})

@app.get("/forecast")
def forecast():
    uplift=float(os.getenv("DEMO_UPLIFT_PCT","2.0")); band=float(os.getenv("DEMO_BAND_PCT","5.0"))
    out=[]
    for r in PRICES:
        p=float(r["price"]); point=round(p*(1+uplift/100),2); low=round(point*(1-band/100),2); high=round(point*(1+band/100),2)
        out.append({"name":r["name"],"unit":r["unit"],"t_plus_1":point,"low":low,"high":high,"conf":0.8})
    return JSONResponse({"generated_at":now(),"forecast":out})
