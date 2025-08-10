# FalconTrade AI (MVP Backend)

Corporate-clean MVP for Azerbaijan's first AI-powered trade intelligence platform.

## Stack
- **Python 3.10+**
- **FastAPI** (API)
- **Uvicorn** (ASGI server)
- **APScheduler** (background jobs)
- **PostgreSQL** (planned; mocked data for preview)

## What’s included (today)
- `/health` — health check
- `/prices` — serves preview commodity prices
- `/forecast` — serves next-day mock forecasts (columns match preview)
- Background scheduler placeholder (15-min job)

> Note: Data is mocked for preview. We’ll wire real scrapers and Postgres next.

## Quickstart (Mac)
```bash
# 1) Clone or unzip this repo, then:
cd backend

# 2) Create & activate venv
python3 -m venv .venv
source .venv/bin/activate

# 3) Install deps
pip install -r requirements.txt

# 4) Run API
uvicorn app.main:app --reload --port 8000

# 5) Open in browser
# http://127.0.0.1:8000/docs  (interactive Swagger)
# http://127.0.0.1:8000/prices
# http://127.0.0.1:8000/forecast
```

## GitHub push (no password sharing)
```bash
# From your local folder:
git init
git add .
git commit -m "FalconTrade AI MVP backend skeleton"
git branch -M main
git remote add origin https://github.com/falcontradeai/falcontrade-ai.git
git push -u origin main
```

## Next steps
- Replace mock loader with real scraper service
- Add Postgres + SQLModel/SQLAlchemy
- Add auth, rate limits, and staging deploy (Railway/Render/DigitalOcean)
