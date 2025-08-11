from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler
from pathlib import Path
import json
import os

# Create the FastAPI application
app = FastAPI(title="FalconTrade AI — MVP Backend with CORS", version="0.1.0")

# Configure CORS middleware to allow the frontend to access the API from any domain.
# You can replace "*" with a list of allowed origins such as ["https://falcontrade-frontend.vercel.app"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specify allowed origins for better security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to the preview data file. Adjust this path according to your project structure.
DATA_PATH = Path(__file__).resolve().parent.parent.parent / "preview" / "falcontrade_preview_api.json"

class Health(BaseModel):
    status: str

def load_preview():
    """Load preview data from the JSON file."""
    if DATA_PATH.exists():
        with open(DATA_PATH, "r") as f:
            return json.load(f)
    return {"error": "preview file not found"}

def background_job():
    """Placeholder background job for periodic tasks (e.g. refreshing data)."""
    # In the preview version, we do nothing. In the future, implement scraping or data refresh here.
    pass

# Setup a scheduler to run background jobs. You can disable this if not needed.
scheduler = BackgroundScheduler()
scheduler.add_job(background_job, "interval", minutes=15, id="refresh_job", replace_existing=True)
try:
    scheduler.start()
except Exception:
    pass

@app.get("/health", response_model=Health)
def health() -> Health:
    """Health check endpoint."""
    return Health(status="ok")

@app.get("/prices")
def prices():
    """Return the latest prices from the preview data."""
    data = load_preview()
    if "commodities" in data:
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
    """Return the next-day forecasts from the preview data."""
    data = load_preview()
    if "commodities" in data:
        return JSONResponse(content={
            "generated_at": data.get("generated_at"),
            "base_currency": data.get("base_currency"),
            "forecasts": [
                {"name": c["name"], "unit": c["unit"], "t_plus_1": c.get("forecast_t_plus_1", 0)}
                for c in data["commodities"]
            ]
        })
    return JSONResponse(content=data, status_code=200)
