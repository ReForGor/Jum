#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    ./venv/bin/pip install --upgrade pip
    ./venv/bin/pip install -r requirements.txt
fi

PORT="${PORT:-8000}"
HOST="${HOST:-0.0.0.0}"

echo "=========================================================="
echo "⚡ Starting TechPrice IT Equipment Price Aggregator & API"
echo "🌐 Web Dashboard: http://localhost:${PORT}"
echo "📊 Comparison:    http://localhost:${PORT}/compare"
echo "🔥 Hot Deals:     http://localhost:${PORT}/deals"
echo "⚡ Scraper Hub:    http://localhost:${PORT}/platforms"
echo "🚀 API Swagger:   http://localhost:${PORT}/docs"
echo "=========================================================="

exec ./venv/bin/uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
