#!/bin/sh
set -e
echo "=== ENTRYPOINT: starting at $(date) ==="
echo "ENV: POSTGRES_HOST=$POSTGRES_HOST, POSTGRES_PORT=$POSTGRES_PORT"

# Ждём доступности базы
python /app/wait_for_db.py

echo "✅ DB is ready — starting Flask..."
exec flask run --host=0.0.0.0 --port=5000
