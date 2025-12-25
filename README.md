# Antarctic Ecosystem Simulation Game

A three-layer architecture Antarctic ecosystem simulator featuring penguins, seals, fish, and environmental interactions.

## Architecture Design

### 1. Simulation Core - Python
- **Location**: `simulation/`
- **Responsibility**: Pure logic computation, no UI dependencies
- **Features**:
  - Time step (tick) system
  - Animal behavior simulation (movement, predation, breeding)
  - Environment state updates (ice melting, temperature changes)
  - State serialization

### 2. Backend Service - FastAPI
- **Location**: `backend/`
- **Responsibility**: Expose simulation core, provide API and WebSocket
- **Features**:
  - REST API: `GET /state`, `POST /step`
  - WebSocket: Real-time state update push
  - State persistence
  - Multi-room support

### 3. Frontend Visualization - React + TypeScript
- **Location**: `frontend/`
- **Responsibility**: Visual rendering and user interaction
- **Features**:
  - Canvas/WebGL rendering
  - Animation interpolation (backend 5 ticks/s, frontend 60fps)
  - WebSocket real-time state reception
  - Control panel (start/pause/reset)

## Quick Start

> **For detailed instructions, see [docs/QUICK_START.md](docs/QUICK_START.md)**

### Using Scripts (Easiest)

**Windows**:
- Double-click `scripts/start_backend.bat` to start backend
- Double-click `scripts/start_frontend.bat` to start frontend

**Linux/Mac**:
```bash
./scripts/start_backend.sh
./scripts/start_frontend.sh
```

### Install Dependencies

**Backend**:
```bash
cd backend
pip install -r requirements.txt
```

**Frontend**:
```bash
cd frontend
npm install
```

### Run

**Start Backend**:
```bash
cd backend
python main.py
```

**Start Frontend**:
```bash
cd frontend
npm start
```

Visit `http://localhost:3000` to view the visualization interface.

### Testing

**Quick Test (Recommended)**:
```bash
python tests/test_quick.py
```

**Full Test Suite**:
```bash
python tests/run_tests.py
# or
python -m unittest discover tests
```

**Run Individual Test Files**:
```bash
python -m unittest tests.test_animals
python -m unittest tests.test_engine
python -m unittest tests.test_integration
```

**Using Scripts**:
```bash
# Windows
scripts\run_tests.bat

# Linux/Mac
./scripts/run_tests.sh
```

Test Coverage:
- ✅ Animal classes (Penguins, Seals, Fish)
- ✅ Environment system
- ✅ Simulation engine
- ✅ State serialization
- ✅ Integration tests

## Data Model

### World State (WorldState)
```python
{
    "tick": 0,
    "animals": {
        "penguins": [...],
        "seals": [...],
        "fish": [...]
    },
    "environment": {
        "ice_coverage": 0.8,
        "temperature": -10,
        "sea_level": 100
    }
}
```

### Animal Attributes
- **Penguins**: Position, energy, state (land/sea), age
- **Seals**: Position, energy, state, age
- **Fish**: Position, energy, age

## API Endpoints

### REST API
- `GET /state` - Get current world state
- `POST /step?n=1` - Advance simulation N steps (n: 1-100)
- `POST /reset` - Reset simulation
- `POST /start` - Start automatic running (5 ticks per second)
- `POST /stop` - Stop automatic running

### WebSocket
- `ws://localhost:8000/ws` - WebSocket connection
  - Automatically receive state updates after connection
  - Send `"step"` to manually advance one step
  - Send `"ping"` to test connection

## Game Mechanics

### Animal Behavior
- **Penguins**:
  - Rest on land, go to sea to catch fish when energy is sufficient
  - Automatically go ashore when energy is below 30
  - Can breed on land (requires pairing)
  
- **Seals**:
  - Mainly active in the sea, occasionally come ashore to rest
  - Prey on penguins and fish
  - Can breed on land
  
- **Fish**:
  - Swim randomly in the sea
  - Preyed upon by penguins and seals
  - Can breed

### Environment System
- Seasonal cycle (4000 ticks per cycle)
- Temperature changes with seasons, affecting ice coverage
- Ice coverage affects land/sea distribution

## Project Structure

```
Antarctica/
├── simulation/          # Simulation core (Python)
│   ├── __init__.py
│   ├── animals.py       # Animal class definitions
│   ├── environment.py   # Environment class definition
│   ├── world.py         # World state
│   └── engine.py        # Simulation engine
├── backend/             # Backend service (FastAPI)
│   ├── main.py          # API server
│   └── requirements.txt
├── frontend/            # Frontend (React + TypeScript)
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── hooks/       # Custom Hooks
│   │   └── types.ts     # Type definitions
│   └── package.json
├── tests/               # Test files
│   ├── test_*.py        # Unit tests
│   └── run_tests.py     # Test runner
├── scripts/             # Startup and utility scripts
│   ├── start_backend.bat/sh
│   ├── start_frontend.bat/sh
│   └── run_tests.bat/sh
├── tools/               # Development tools
│   └── *.py, *.js       # Utility scripts
├── docs/                # Documentation
│   ├── QUICK_START.md
│   ├── RUN_GUIDE.md
│   ├── ARCHITECTURE.md
│   └── TESTING.md
└── README.md
```

## Development Plan

- [x] Project structure design
- [x] Simulation core implementation
- [x] Backend API implementation
- [x] Frontend visualization implementation
- [x] Animation system
- [ ] Performance optimization
- [ ] More animal types
- [ ] Save/load functionality
- [ ] Statistics charts
