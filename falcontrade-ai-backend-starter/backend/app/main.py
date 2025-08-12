from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, timezone

app = FastAPI(title="FalconTrade API")

# allow requests from your site (open for now)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PRICES = [
    {"name": "Wheat", "unit": "$/ton", "price": 250.0, "source": "Preview"},
    {"name": "Barley", "unit": "$/ton", "price": 220.0, "source": "Preview"},
    {"name": "Sunflower Oil", "unit": "$/ton", "price": 980.0, "source": "Preview"},
    {"name": "Sugar", "unit": "$/ton", "price": 570.0, "source": "Preview"},
    {"name": "Steel", "unit": "$/ton", "price": 600.0, "source": "Preview"},
]

@app.get("/prices")
def prices():
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "base_currency": "USD",
        "prices": PRICES,
    }

# demo forecast so UI fills immediately
@app.get("/forecast")
def forecast():
    fc = [
        {"name": r["name"], "unit": r["unit"], "t_plus_1": round(float(r["price"]) * 1.02, 2)}
        for r in PRICES
    ]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "forecast": fc,
    }
