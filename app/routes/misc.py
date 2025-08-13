from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/version")
def version():
    return {"name": "FalconTrade API", "version": "v1.0", "deployed_at": datetime.now(timezone.utc).isoformat()}

@router.get("/categories")
def categories():
    return ["fertilizer","grain","oils","textiles","panels","poultry","fruits","metals"]
