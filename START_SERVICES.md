# Starting Backend and Frontend Services

## Quick Start

### Windows Users (Easiest)

1. **Start Backend**:
   - Double-click `scripts\start_backend.bat`
   - Wait to see "Uvicorn running on http://0.0.0.0:8000"

2. **Start Frontend** (Open a new window):
   - Double-click `scripts\start_frontend.bat`
   - Wait to see "Compiled successfully!"

3. **Access Application**:
   - Browser will open automatically, or manually visit `http://localhost:3000`

### Linux/Mac Users

1. **Start Backend**:
   ```bash
   chmod +x scripts/start_backend.sh
   ./scripts/start_backend.sh
   ```

2. **Start Frontend** (New terminal):
   ```bash
   chmod +x scripts/start_frontend.sh
   ./scripts/start_frontend.sh
   ```

3. **Access Application**:
   - Browser visit `http://localhost:3000`

## Manual Start

### Backend

```bash
cd backend
# First run needs to create virtual environment
py -m venv venv
venv\Scripts\activate  # Windows
# or source venv/bin/activate  # Linux/Mac

# Install dependencies (first run)
pip install -r requirements.txt

# Start service
python main.py
```

Backend will start at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend

# Install dependencies (first run)
npm install

# Start development server
npm start
```

Frontend will start at `http://localhost:3000`

## Verify Service Running

### Check Backend
- Visit `http://localhost:8000/state` should return JSON data
- Visit `http://localhost:8000/docs` to view API documentation

### Check Frontend
- Visit `http://localhost:3000` should see visualization interface
- Console should show WebSocket connection successful

## Stop Services

- Press `Ctrl+C` in the terminal window running the service

## Troubleshooting

If you encounter problems, please check:
- `docs/RUN_GUIDE.md` - Detailed run guide
- `docs/TROUBLESHOOTING.md` - Troubleshooting guide
