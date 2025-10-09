#!/bin/bash
# Start EcoMind API

cd /Users/jianphua/projects/EcoMind/api

# Activate virtual environment
source venv/bin/activate

# Load environment variables
if [ -f ".env.local" ]; then
    export DATABASE_URL="postgresql://ecomind:ecomind_dev_pass@localhost:5432/ecomind"
    export JWT_SECRET="kDXgYrwOJRqfTvg9YP7JtJmlIPumsltMf1rn1fK8pW8"
    export ACCESS_TOKEN_EXPIRE_MINUTES="60"
    export PYTHONPATH="/Users/jianphua/projects/EcoMind/api"
fi

# Start API on port 8001 (8000 may be in use)
uvicorn app.main:app --host 0.0.0.0 --port 8001 >> api.log 2>&1 &
PID=$!
echo $PID > api.pid

echo "API started with PID: $PID"
echo "Logs: tail -f api.log"
