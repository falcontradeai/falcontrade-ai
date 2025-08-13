#!/usr/bin/env bash
set -e
export PORT=${PORT:-8000}
# Use bash to avoid needing executable bit when Render runs the command
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
