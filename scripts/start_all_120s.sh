#!/bin/bash

# ========================================
# Start both backend and frontend, then
# auto-close after 120 seconds
# ========================================
RUN_DURATION=120

cleanup() {
    echo ""
    echo "Shutting down..."
    kill $FRONTEND_PID 2>/dev/null
    lsof -ti:3000 | xargs kill -9 2>/dev/null
    pkill -f node 2>/dev/null
    kill $BACKEND_PID 2>/dev/null
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    echo "All services stopped."
    exit 0
}
trap cleanup SIGINT SIGTERM

echo "========================================"
echo "Starting Backend and Frontend"
echo "Will auto-close after $RUN_DURATION seconds"
echo "========================================"
echo ""

# Change to project root directory
cd "$(dirname "$0")/.."

# ---- Step 1: Prepare and start Backend ----
echo "[1/2] Starting Backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

if [ ! -f "venv/bin/fastapi" ]; then
    echo "Installing backend dependencies..."
    pip install -r requirements.txt
fi

echo "Starting backend on http://localhost:8000"
python main.py &
BACKEND_PID=$!
cd ..

sleep 2

# ---- Step 2: Prepare and start Frontend ----
echo ""
echo "[2/2] Starting Frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

export BROWSER=none
echo "Starting frontend on http://localhost:3000"
npm start &
FRONTEND_PID=$!
cd ..

sleep 5

# ---- Step 3: Wait then cleanup ----
echo ""
echo "========================================"
echo "Both services are running!"
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Waiting $RUN_DURATION seconds before auto-closing..."
echo "Press Ctrl+C to stop early"
echo "========================================"
echo ""

sleep $RUN_DURATION

# Cleanup
echo ""
echo "Shutting down..."
kill $FRONTEND_PID 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null
pkill -f node 2>/dev/null
kill $BACKEND_PID 2>/dev/null
lsof -ti:8000 | xargs kill -9 2>/dev/null
echo ""
echo "========================================"
echo "All services stopped"
echo "========================================"
