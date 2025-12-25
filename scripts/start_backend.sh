#!/bin/bash

# ========================================
# Auto-close timer (in seconds)
# Set to 0 to disable auto-close (run forever)
# Default: 60 seconds (1 minute)
# ========================================
AUTO_CLOSE=60

echo "========================================"
echo "Starting Backend Server..."
if [ "$AUTO_CLOSE" -eq 0 ]; then
    echo "Auto-close: DISABLED (will run until manually stopped)"
else
    echo "Auto-close: ENABLED (will close after $AUTO_CLOSE seconds)"
fi
echo "========================================"

# Change to project root directory
cd "$(dirname "$0")/.."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/bin/fastapi" ]; then
    pip install -r requirements.txt
fi

echo ""
echo "Starting server..."
echo "Backend URL: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""

if [ "$AUTO_CLOSE" -eq 0 ]; then
    echo "Press Ctrl+C to stop the server"
else
    echo "Server will auto-close after $AUTO_CLOSE seconds"
    echo "Press Ctrl+C to stop the server manually"
fi

echo "========================================"
echo ""

# Start server in background
python main.py &
SERVER_PID=$!

# Wait for auto-close timer (if enabled)
if [ "$AUTO_CLOSE" -ne 0 ]; then
    echo "Waiting $AUTO_CLOSE seconds before auto-closing..."
    sleep $AUTO_CLOSE
    echo ""
    echo "Auto-closing server..."
    kill $SERVER_PID 2>/dev/null
    # Also kill by port 8000
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    echo "Server closed."
else
    # Wait for server to finish
    wait $SERVER_PID
fi

