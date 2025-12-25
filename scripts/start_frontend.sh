#!/bin/bash
echo "Starting Frontend..."
# Change to project root directory
cd "$(dirname "$0")/.."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi
npm start

