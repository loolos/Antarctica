# Run Guide

## Quick Start

### Method 1: Using Startup Scripts (Recommended)

#### Windows Users

**Step 1: Start Backend**
```bash
# Double-click to run, or execute in command line:
start_backend.bat
```

**Step 2: Start Frontend (Open a new terminal)**
```bash
# Double-click to run, or execute in command line:
start_frontend.bat
```

#### Linux/Mac Users

**Step 1: Start Backend**
```bash
chmod +x start_backend.sh
./start_backend.sh
```

**Step 2: Start Frontend (Open a new terminal)**
```bash
chmod +x start_frontend.sh
./start_frontend.sh
```

---

### Method 2: Manual Run

#### 1. Start Backend Service

**First Run (Need to install dependencies)**:
```bash
cd backend
py -m venv venv
venv\Scripts\activate        # Windows
# or source venv/bin/activate  # Linux/Mac
py -m pip install -r requirements.txt
py main.py
```

**Subsequent Runs (Dependencies installed)**:
```bash
cd backend
venv\Scripts\activate        # Windows
# or source venv/bin/activate  # Linux/Mac
py main.py
```

Backend will start at `http://localhost:8000`

**Verify Backend Running**:
- Open browser and visit: `http://localhost:8000/docs` (FastAPI auto documentation)
- Or visit: `http://localhost:8000/state` (Get current state)

#### 2. Start Frontend (Open a new terminal)

**First Run (Need to install dependencies)**:
```bash
cd frontend
npm install
npm start
```

**Subsequent Runs (Dependencies installed)**:
```bash
cd frontend
npm start
```

Frontend will start at `http://localhost:3000`

Browser will open automatically, if not, manually visit `http://localhost:3000`

---

## Run Order

1. **Start Backend First** (Port 8000)
   - Wait to see "Uvicorn running on http://0.0.0.0:8000"

2. **Then Start Frontend** (Port 3000)
   - Wait to see "Compiled successfully!"

3. **Access Frontend Interface**
   - Browser will automatically open `http://localhost:3000`
   - Or manually visit that address

---

## Usage Instructions

### Control Panel
- **Start**: Start automatic simulation (5 ticks per second)
- **Stop**: Stop automatic simulation
- **Reset**: Reset simulation to initial state
- **Step**: Manually advance one step

### Visualization Interface
- Left side: Land (gray)
- Right side: Sea (blue)
- White/light blue dots: Penguins
- Brown/dark brown ellipses: Seals
- Blue small dots: Fish
- Top display: Current tick, animal counts, temperature, ice coverage

---

## Common Issues

### 1. Backend Startup Failure

**Issue**: `ModuleNotFoundError: No module named 'fastapi'`
**Solution**: 
```bash
cd backend
py -m pip install -r requirements.txt
```

**Issue**: Port 8000 is occupied
**Solution**: Modify the last line of `backend/main.py`, change to another port:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # Change to 8001
```

### 2. Frontend Startup Failure

**Issue**: `npm: command not found`
**Solution**: Install Node.js: https://nodejs.org/

**Issue**: Port 3000 is occupied
**Solution**: Frontend will automatically try the next port (3001, 3002...)

**Issue**: `npm install` is slow or fails
**Solution**: Use a mirror:
```bash
npm config set registry https://registry.npmmirror.com
npm install
```

### 3. Frontend Cannot Connect to Backend

**Issue**: WebSocket connection fails
**Solution**: 
- Ensure backend is started
- Check if backend address is `http://localhost:8000`
- Check browser console for error messages

### 4. Encoding Issues (Windows)

If you see garbled text, ensure terminal uses UTF-8 encoding:
```bash
chcp 65001
```

---

## API Testing

### Using Browser

1. **Get State**: `http://localhost:8000/state`
2. **API Documentation**: `http://localhost:8000/docs`
3. **Interactive API**: `http://localhost:8000/redoc`

### Using curl

```bash
# Get state
curl http://localhost:8000/state

# Advance one step
curl -X POST http://localhost:8000/step?n=1

# Reset
curl -X POST http://localhost:8000/reset

# Start automatic running
curl -X POST http://localhost:8000/start

# Stop
curl -X POST http://localhost:8000/stop
```

---

## Development Mode

### Backend Hot Reload
Modify the last line of `backend/main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

### Frontend Hot Reload
Frontend supports hot reload by default, automatically refreshes after code changes.

---

## Stop Services

- **Backend**: Press `Ctrl+C` in the terminal running backend
- **Frontend**: Press `Ctrl+C` in the terminal running frontend

---

## Next Steps

- View `README.md` to understand project architecture
- View `ARCHITECTURE.md` for design details
- View `TESTING.md` to learn how to run tests
