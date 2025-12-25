"""
Backend service - FastAPI
Provides REST API and WebSocket interfaces
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
import json
from typing import List
import sys
import os

# Add simulation module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from simulation.engine import SimulationEngine
from simulation.world import WorldState


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

# Global simulation engine instance
simulation_engine = SimulationEngine()
is_running = False
simulation_speed = 1.0  # Speed multiplier (1.0 = normal, 5 ticks/sec)
websocket_clients: List[WebSocket] = []


@app.get("/")
async def root():
    """Root path"""
    return {"message": "Antarctic Ecosystem Simulation API", "version": "1.0.0"}


@app.get("/state")
async def get_state():
    """Get current world state"""
    state = simulation_engine.get_state()
    return state.to_dict()


@app.post("/step")
async def step(n: int = 1):
    """Advance simulation N steps"""
    if n < 1 or n > 100:
        return JSONResponse(
            status_code=400,
            content={"error": "n must be between 1 and 100"}
        )
    
    simulation_engine.step(n)
    state = simulation_engine.get_state()
    return state.to_dict()


@app.post("/reset")
async def reset():
    """Reset simulation"""
    global simulation_engine
    simulation_engine = SimulationEngine()
    return {"message": "Simulation reset"}


@app.post("/start")
async def start():
    """Start automatic running"""
    global is_running
    is_running = True
    return {"message": "Simulation started"}


@app.post("/stop")
async def stop():
    """Stop automatic running"""
    global is_running
    is_running = False
    return {"message": "Simulation stopped"}


@app.post("/speed")
async def set_speed(request: SpeedRequest):
    """Set simulation speed multiplier
    
    Args:
        request: JSON body with speed field (0.1 to 10.0, where 1.0 = normal speed, 5 ticks/sec)
    """
    global simulation_speed
    speed = request.speed
    if speed < 0.1 or speed > 10.0:
        return JSONResponse(
            status_code=400,
            content={"error": "Speed must be between 0.1 and 10.0"}
        )
    simulation_speed = speed
    return {"message": f"Speed set to {speed}x", "speed": speed}


@app.get("/speed")
async def get_speed():
    """Get current simulation speed"""
    return {"speed": simulation_speed}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint, push state updates in real-time"""
    await websocket.accept()
    websocket_clients.append(websocket)
    
    try:
        # Send initial state
        state = simulation_engine.get_state()
        await websocket.send_json(state.to_dict())
        
        # Keep connection, wait for client messages
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
            elif data == "step":
                simulation_engine.step(1)
                state = simulation_engine.get_state()
                await websocket.send_json(state.to_dict())
    except WebSocketDisconnect:
        websocket_clients.remove(websocket)


async def background_simulation():
    """Background simulation task with configurable speed"""
    global is_running, simulation_speed
    base_interval = 0.2  # Base interval for 1.0x speed (5 ticks per second)
    
    while True:
        if is_running:
            simulation_engine.step(1)
            # Broadcast to all WebSocket clients
            state = simulation_engine.get_state()
            state_dict = state.to_dict()
            
            disconnected = []
            for client in websocket_clients:
                try:
                    await client.send_json(state_dict)
                except:
                    disconnected.append(client)
            
            # Remove disconnected clients
            for client in disconnected:
                if client in websocket_clients:
                    websocket_clients.remove(client)
        
        # Calculate sleep interval based on speed multiplier
        # Higher speed = shorter interval = more ticks per second
        # speed = 1.0 -> 0.2s interval -> 5 ticks/sec
        # speed = 2.0 -> 0.1s interval -> 10 ticks/sec
        # speed = 0.5 -> 0.4s interval -> 2.5 ticks/sec
        sleep_interval = base_interval / simulation_speed
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

