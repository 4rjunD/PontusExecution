#!/bin/bash
# Start script for Render deployment
cd "$(dirname "$0")" || exit 1
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"

