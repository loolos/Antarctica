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


@app.get("/")
async def root():
    """Root path"""
    return {"message": "Antarctic Ecosystem Simulation API", "version": "1.0.0"}


@app.get("/state")
async def get_state(service: SimulationService = Depends(get_simulation_service)):
    """Get current world state"""
    state = service.get_state()
    return state.to_dict()


@app.post("/step")
async def step(n: int = 1, service: SimulationService = Depends(get_simulation_service)):
    """Advance simulation N steps"""
    try:
        service.step(n)
        state = service.get_state()
        return state.to_dict()
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"error": str(e)}
        )


@app.post("/reset")
async def reset(service: SimulationService = Depends(get_simulation_service)):
    """Reset simulation"""
    service.reset()
    return {"message": "Simulation reset"}


@app.post("/start")
async def start(service: SimulationService = Depends(get_simulation_service)):
    """Start automatic running"""
    service.start()
    return {"message": "Simulation started"}


@app.post("/stop")
async def stop(service: SimulationService = Depends(get_simulation_service)):
    """Stop automatic running"""
    service.stop()
    return {"message": "Simulation stopped"}


@app.post("/speed")
async def set_speed(
    request: SpeedRequest,
    service: SimulationService = Depends(get_simulation_service)
):
    """Set simulation speed multiplier
    
    Args:
        request: JSON body with speed field (0.1 to 10.0, where 1.0 = normal speed, 5 ticks/sec)
    """
    try:
        service.set_speed(request.speed)
        return {"message": f"Speed set to {request.speed}x", "speed": request.speed}
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"error": str(e)}
        )


@app.get("/speed")
async def get_speed(service: SimulationService = Depends(get_simulation_service)):
    """Get current simulation speed"""
    return {"speed": service.get_speed()}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint, push state updates in real-time"""
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

