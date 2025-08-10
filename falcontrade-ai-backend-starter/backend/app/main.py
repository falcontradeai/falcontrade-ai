from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler
from pathlib import Path
import json, os

app = FastAPI(title="FalconTrade AI — MVP Backend", version="0.1.0")

DATA_PATH = Path(__file__).resolve().parent.parent.parent / "preview" / "falcontrade_preview_api.json"

class Health(BaseModel):
    status: str

def load_preview():
    if DATA_PATH.exists():
        with open(DATA_PATH, "r") as f:
            return json.load(f)
    return {"error": "preview file not found"}

def background_job():
    # Placeholder: where we will refresh prices/scrape every 15 minutes
    # In MVP preview mode we do nothing
    pass

# Start scheduler (disabled on import by some servers; keep simple for dev)
scheduler = BackgroundScheduler()
scheduler.add_job(background_job, "interval", minutes=15, id="refresh_job", replace_existing=True)
try:
    scheduler.start()
except Exception:
    pass

@app.get("/health", response_model=Health)
def health():
    return Health(status="ok")

@app.get("/prices")
def prices():
    data = load_preview()
    if "commodities" in data:
        # Return only current prices (compact format)
        return JSONResponse(content={
            "generated_at": data.get("generated_at"),
            "base_currency": data.get("base_currency"),
            "prices": [
                {"name": c["name"], "unit": c["unit"], "price": c["price"]}
                for c in data["commodities"]
            ]
        })
    return JSONResponse(content=data, status_code=200)

@app.get("/forecast")
def forecast():
    data = load_preview()
    if "commodities" in data:
        return JSONResponse(content={
            "generated_at": data.get("generated_at"),
            "base_currency": data.get("base_currency"),
            "forecasts": [
                {"name": c["name"], "unit": c["unit"], "t_plus_1": c["forecast_t_plus_1"]}
                for c in data["commodities"]
            ]
        })
    return JSONResponse(content=data, status_code=200)
