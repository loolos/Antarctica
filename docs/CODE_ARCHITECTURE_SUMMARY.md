# Code Architecture Summary

## 1) Overall layering

The project follows a 3-layer architecture:

1. **Simulation Core (`simulation/`)**
   - Pure Python simulation logic, independent from UI and HTTP.
   - Maintains world state (`WorldState`), environment, and animal lifecycle.
2. **Backend Service (`backend/`)**
   - FastAPI + WebSocket facade around the simulation core.
   - Exposes state/query/control APIs and real-time state pushes.
3. **Frontend (`frontend/`)**
   - React + TypeScript + Canvas rendering.
   - Receives state snapshots and renders smooth 60fps interpolation.

## 2) Core execution flow

### Auto-run flow

- Frontend connects to backend WebSocket `/ws`.
- Backend background task periodically calls `service.step(1)` while running.
- Service delegates to `SimulationEngine.step()`.
- Engine runs tick loop: environment update, animal updates, predation, breeding, spawning, dead cleanup.
- Backend broadcasts serialized world state to all WebSocket clients.
- Frontend updates target positions and interpolates movement in render loop.

### Manual step flow

- Frontend sends `"step"` message via WebSocket.
- Backend executes one simulation step and returns updated state.

## 3) Responsibilities by key files

- `simulation/engine.py`: central world update loop and behavior orchestration.
- `simulation/animals.py`: species definitions, basic state transitions, energy/age lifecycle.
- `simulation/environment.py`: sea/land and climate-related world parameters.
- `backend/service.py`: simulation lifecycle control (start/stop/reset/speed).
- `backend/main.py`: REST + WebSocket API surface and background loop.
- `frontend/src/hooks/useWebSocket.ts`: connection lifecycle, reconnection, state receiving.
- `frontend/src/components/SimulationCanvas.tsx`: canvas drawing and interpolation.

## 4) Notable design choices

- **Simulation tick rate and render rate decoupled**:
  backend updates in coarse ticks, frontend animates continuously.
- **Centralized config (`simulation/config.py`)**:
  behavior thresholds and balancing parameters are managed in one place.
- **Service facade pattern**:
  keeps API layer thin and simulation core reusable.

## 5) Testing and quality signals

- Unit and integration tests exist under `tests/` for animals, environment, engine, and full-cycle behavior.
- Recommended fast check: `python tests/test_quick.py`.
- Full suite: `python -m unittest discover tests`.
