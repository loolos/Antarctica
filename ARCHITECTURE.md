# Architecture Design Document

## Overview

This project adopts a three-layer architecture design, completely separating simulation logic, backend services, and frontend visualization for easy maintenance and extension.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│              Frontend (React + TS)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Canvas Render│  │WebSocket Client│ │ Control Panel │ │
│  │  60fps Anim  │  │ Real-time State│ │ Start/Stop    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└───────────────────────┬─────────────────────────────────┘
                        │ WebSocket / REST API
┌───────────────────────▼─────────────────────────────────┐
│            Backend Service (FastAPI)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  REST API    │  │  WebSocket   │  │ Background   │ │
│  │  GET /state  │  │  /ws         │  │  5 tick/s    │ │
│  │  POST /step  │  │              │  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└───────────────────────┬─────────────────────────────────┘
                        │ Call
┌───────────────────────▼─────────────────────────────────┐
│         Simulation Core (Python)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Sim Engine   │  │ Animal Class │  │ Environment  │ │
│  │  tick()      │  │Penguin/Seal/ │  │ Temp/Ice     │ │
│  │  step()      │  │    Fish      │  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Initialization Flow
```
Frontend starts → Connect WebSocket → Backend sends initial state → Frontend renders
```

### 2. Runtime Flow
```
Backend background task (every 200ms)
  ↓
Simulation engine.tick()
  ↓
Update world state
  ↓
Broadcast to all clients via WebSocket
  ↓
Frontend receives state
  ↓
Update animation target positions
  ↓
Canvas render loop (60fps)
  ↓
Smooth interpolation display
```

### 3. Manual Control Flow
```
User clicks "Step" button
  ↓
Frontend sends "step" message to WebSocket
  ↓
Backend executes simulation_engine.step(1)
  ↓
Return new state
  ↓
Frontend updates display
```

## Core Class Design

### SimulationEngine
- **Responsibility**: Simulation core logic
- **Methods**:
  - `tick()`: Execute one time step
  - `step(n)`: Advance N steps
  - `get_state()`: Get current state

### WorldState
- **Responsibility**: Store world state
- **Attributes**:
  - `tick`: Current time step
  - `penguins/seals/fish`: Animal lists
  - `environment`: Environment state
- **Methods**:
  - `to_dict()`: Serialize to JSON

### Animal (Base Class)
- **Attributes**: id, x, y, energy, age
- **Methods**: move(), tick(), is_alive()

### Penguin / Seal / Fish
- Inherit from Animal
- Each implements specific behavior logic

## Performance Considerations

### Backend
- Simulation engine: Pure Python, no external dependencies
- WebSocket broadcast: Async processing, doesn't block main loop
- State serialization: Only when needed

### Frontend
- Canvas rendering: Uses requestAnimationFrame, 60fps
- Animation interpolation: Uses useRef to avoid unnecessary re-renders
- WebSocket: Auto-reconnect mechanism

## Extensibility

### Adding New Animal Types
1. Create new class in `simulation/animals.py`
2. Add update logic in `SimulationEngine`
3. Add rendering logic in frontend `SimulationCanvas`

### Adding New Environmental Factors
1. Extend Environment class in `simulation/environment.py`
2. Apply environmental effects in simulation engine
3. Display in frontend visualization

### Adding New Features
- Save/Load: Add state persistence in backend
- Statistics charts: Add chart components in frontend
- Multi-room: Add room management in backend

## Technology Selection Rationale

### Python (Simulation Core)
- ✅ Easy to implement complex logic
- ✅ Rich scientific computing libraries (if needed)
- ✅ Rapid development

### FastAPI (Backend)
- ✅ High-performance async framework
- ✅ Built-in WebSocket support
- ✅ Auto API documentation

### React + TypeScript (Frontend)
- ✅ Type safety
- ✅ Component-based development
- ✅ Rich ecosystem

### Canvas (Rendering)
- ✅ High-performance 2D rendering
- ✅ Full control over drawing process
- ✅ Suitable for rendering many objects
