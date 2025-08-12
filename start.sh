#!/usr/bin/env bash
set -e
export HOST=${HOST:-0.0.0.0}
export PORT=${PORT:-8000}
uvicorn main:app --host $HOST --port $PORT