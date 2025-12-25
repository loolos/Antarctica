#!/bin/bash

# ========================================
# Auto-close timer (in seconds)
# Set to 0 to disable auto-close (run forever)
# Default: 60 seconds (1 minute)
# ========================================
AUTO_CLOSE=60

echo "========================================"
echo "Starting Frontend Service..."
if [ "$AUTO_CLOSE" -eq 0 ]; then
    echo "Auto-close: DISABLED (will run until manually stopped)"
else
    echo "Auto-close: ENABLED (will close after $AUTO_CLOSE seconds)"
fi
echo "========================================"

# Change to project root directory
cd "$(dirname "$0")/.."
cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

echo ""
echo "Starting development server..."
echo "Frontend will be available at: http://localhost:3000"
echo ""

if [ "$AUTO_CLOSE" -eq 0 ]; then
    echo "Keep this window open while the server is running"
    echo "Press Ctrl+C to stop the server"
else
    echo "Server will auto-close after $AUTO_CLOSE seconds"
    echo "Press Ctrl+C to stop the server manually"
fi

echo "========================================"
echo ""

# Prevent browser from auto-opening
export BROWSER=none

# Start npm in background
npm start &
NPM_PID=$!

# Wait for auto-close timer (if enabled)
if [ "$AUTO_CLOSE" -ne 0 ]; then
    echo "Waiting $AUTO_CLOSE seconds before auto-closing..."
    sleep $AUTO_CLOSE
    echo ""
    echo "Auto-closing server..."
    kill $NPM_PID 2>/dev/null
    # Also kill by port 3000
    lsof -ti:3000 | xargs kill -9 2>/dev/null
    # Kill all node processes
    pkill -f node 2>/dev/null
    echo "Server closed."
else
    # Wait for npm to finish
    wait $NPM_PID
fi

