"""
Backend service - FastAPI
Provides REST API and WebSocket interfaces
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
from typing import List
import sys
import os

# Add simulation module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.service import SimulationService


class SpeedRequest(BaseModel):
    speed: float


app = FastAPI(title="Antarctic Ecosystem Simulation API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global simulation service instance (singleton pattern)
_simulation_service: SimulationService = None


def get_simulation_service() -> SimulationService:
    """Dependency injection for simulation service"""
    global _simulation_service
    if _simulation_service is None:
        _simulation_service = SimulationService()
    return _simulation_service


@app.get("/", tags=["Info"])
async def root():
    """
    Root endpoint - API information
    
    Returns basic information about the API including version.
    
    Returns:
        dict: API information with message and version
    """
    return {"message": "Antarctic Ecosystem Simulation API", "version": "1.0.0"}


@app.get("/state", tags=["Simulation"])
async def get_state(service: SimulationService = Depends(get_simulation_service)):
    """
    Get current world state
    
    Retrieves the complete current state of the simulation world, including:
    - All animals (penguins, seals, fish) with their positions, energy, age, and states
    - Environment state (temperature, ice coverage, season, ice floes)
    - Current simulation tick
    
    Returns:
        dict: Complete world state as a dictionary
        
    Example:
        ```json
        {
            "tick": 100,
            "penguins": [...],
            "seals": [...],
            "fish": [...],
            "environment": {...}
        }
        ```
    """
    state = service.get_state()
    return state.to_dict()


@app.post("/step", tags=["Simulation"])
async def step(
    n: int = 1,
    service: SimulationService = Depends(get_simulation_service)
):
    """
    Advance simulation N steps
    
    Manually advances the simulation by the specified number of steps.
    Each step executes one tick of the simulation, updating all animals,
    environment, and handling interactions.
    
    Args:
        n: Number of steps to advance (1-100, default: 1)
        
    Returns:
        dict: Updated world state after advancing
        
    Raises:
        400: If n is outside valid range (1-100)
        
    Example:
        ```bash
        POST /step?n=10
        ```
    """
    try:
        service.step(n)
        state = service.get_state()
        return state.to_dict()
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"error": str(e)}
        )


@app.post("/reset", tags=["Simulation"])
async def reset(service: SimulationService = Depends(get_simulation_service)):
    """
    Reset simulation to initial state
    
    Resets the entire simulation to its initial state, including:
    - All animals reset to starting positions and states
    - Environment reset to initial conditions
    - Simulation tick reset to 0
    - Automatic running stopped
    
    Returns:
        dict: Success message
        
    Example:
        ```bash
        POST /reset
        ```
    """
    service.reset()
    return {"message": "Simulation reset"}


@app.post("/start", tags=["Control"])
async def start(service: SimulationService = Depends(get_simulation_service)):
    """
    Start automatic simulation
    
    Starts the automatic simulation loop. The simulation will run continuously
    at the configured speed (default: 5 ticks per second) until stopped.
    State updates are automatically broadcast to all connected WebSocket clients.
    
    Returns:
        dict: Success message
        
    Note:
        The simulation runs in the background. Use /stop to halt execution.
    """
    service.start()
    return {"message": "Simulation started"}


@app.post("/stop", tags=["Control"])
async def stop(service: SimulationService = Depends(get_simulation_service)):
    """
    Stop automatic simulation
    
    Stops the automatic simulation loop. The simulation state is preserved
    and can be resumed by calling /start again.
    
    Returns:
        dict: Success message
    """
    service.stop()
    return {"message": "Simulation stopped"}


@app.post("/speed", tags=["Control"])
async def set_speed(
    request: SpeedRequest,
    service: SimulationService = Depends(get_simulation_service)
):
    """
    Set simulation speed multiplier
    
    Adjusts the speed at which the simulation runs. The speed is a multiplier
    that affects how fast the simulation advances.
    
    Args:
        request: JSON body containing speed field
            - speed (float): Speed multiplier (0.1 to 10.0)
                - 0.1 = 10% speed (0.5 ticks/sec)
                - 1.0 = normal speed (5 ticks/sec)
                - 2.0 = 2x speed (10 ticks/sec)
                - 10.0 = 10x speed (50 ticks/sec)
    
    Returns:
        dict: Success message with new speed
        
    Raises:
        400: If speed is outside valid range (0.1-10.0)
        
    Example:
        ```json
        POST /speed
        {
            "speed": 2.0
        }
        ```
    """
    try:
        service.set_speed(request.speed)
        return {"message": f"Speed set to {request.speed}x", "speed": request.speed}
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"error": str(e)}
        )


@app.get("/speed", tags=["Control"])
async def get_speed(service: SimulationService = Depends(get_simulation_service)):
    """
    Get current simulation speed
    
    Returns the current speed multiplier of the simulation.
    
    Returns:
        dict: Current speed multiplier
        
    Example:
        ```json
        {
            "speed": 1.0
        }
        ```
    """
    return {"speed": service.get_speed()}


@app.websocket("/ws", tags=["WebSocket"])
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time state updates
    
    Establishes a WebSocket connection for receiving real-time simulation
    state updates. When automatic simulation is running, state updates
    are automatically pushed to all connected clients.
    
    **Connection Flow:**
    1. Client connects to `/ws`
    2. Server sends initial world state immediately
    3. If simulation is running, server pushes updates automatically
    4. Client can send commands:
       - `"ping"`: Test connection (server responds with `"pong"`)
       - `"step"`: Manually advance simulation by 1 step
    
    **State Update Format:**
    State updates are sent as JSON objects matching the `/state` endpoint format.
    
    **Disconnection:**
    Client is automatically removed from the broadcast list on disconnect.
    
    Example:
        ```javascript
        const ws = new WebSocket('ws://localhost:8000/ws');
        ws.onmessage = (event) => {
            const state = JSON.parse(event.data);
            console.log('Tick:', state.tick);
        };
        ws.send('ping');  // Test connection
        ws.send('step');  // Advance one step
        ```
    """
    await websocket.accept()
    service = get_simulation_service()
    service.add_websocket_client(websocket)
    
    try:
        # Send initial state
        state = service.get_state()
        await websocket.send_json(state.to_dict())
        
        # Keep connection, wait for client messages
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
            elif data == "step":
                service.step(1)
                state = service.get_state()
                await websocket.send_json(state.to_dict())
    except WebSocketDisconnect:
        service.remove_websocket_client(websocket)


async def background_simulation():
    """Background simulation task with configurable speed"""
    service = get_simulation_service()
    base_interval = 0.2  # Base interval for 1.0x speed (5 ticks per second)
    
    while True:
        if service.is_running:
            service.step(1)
            # Broadcast to all WebSocket clients
            state = service.get_state()
            state_dict = state.to_dict()
            
            disconnected = []
            for client in service.get_websocket_clients():
                try:
                    await client.send_json(state_dict)
                except:
                    disconnected.append(client)
            
            # Remove disconnected clients
            for client in disconnected:
                service.remove_websocket_client(client)
        
        # Calculate sleep interval based on speed multiplier
        # Higher speed = shorter interval = more ticks per second
        # speed = 1.0 -> 0.2s interval -> 5 ticks/sec
        # speed = 2.0 -> 0.1s interval -> 10 ticks/sec
        # speed = 0.5 -> 0.4s interval -> 2.5 ticks/sec
        sleep_interval = base_interval / service.speed
        # Clamp to reasonable bounds (min 0.01s, max 2.0s)
        sleep_interval = max(0.01, min(2.0, sleep_interval))
        await asyncio.sleep(sleep_interval)


@app.on_event("startup")
async def startup_event():
    """Create background task on startup"""
    asyncio.create_task(background_simulation())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

