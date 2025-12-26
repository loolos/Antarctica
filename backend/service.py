"""
Simulation service - manages simulation state and operations
"""
from typing import List, Optional
from fastapi import WebSocket
import sys
import os

# Add simulation module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from simulation.engine import SimulationEngine


class SimulationService:
    """Service class for managing simulation state"""
    
    def __init__(self, width: int = 800, height: int = 600):
        """Initialize simulation service"""
        self.engine = SimulationEngine(width=width, height=height)
        self.is_running = False
        self.speed = 1.0  # Speed multiplier (1.0 = normal, 5 ticks/sec)
        self.websocket_clients: List[WebSocket] = []
    
    def start(self):
        """Start automatic simulation"""
        self.is_running = True
    
    def stop(self):
        """Stop automatic simulation"""
        self.is_running = False
    
    def set_speed(self, speed: float):
        """Set simulation speed multiplier
        
        Args:
            speed: Speed multiplier (0.1 to 10.0)
            
        Raises:
            ValueError: If speed is out of valid range
        """
        if speed < 0.1 or speed > 10.0:
            raise ValueError("Speed must be between 0.1 and 10.0")
        self.speed = speed
    
    def get_speed(self) -> float:
        """Get current simulation speed"""
        return self.speed
    
    def reset(self):
        """Reset simulation to initial state"""
        width = self.engine.world.environment.width
        height = self.engine.world.environment.height
        self.engine = SimulationEngine(width=width, height=height)
        self.is_running = False
    
    def get_state(self):
        """Get current world state"""
        return self.engine.get_state()
    
    def step(self, n: int = 1):
        """Advance simulation N steps
        
        Args:
            n: Number of steps (1-100)
            
        Raises:
            ValueError: If n is out of valid range
        """
        if n < 1 or n > 100:
            raise ValueError("n must be between 1 and 100")
        self.engine.step(n)
    
    def add_websocket_client(self, client: WebSocket):
        """Add a WebSocket client"""
        if client not in self.websocket_clients:
            self.websocket_clients.append(client)
    
    def remove_websocket_client(self, client: WebSocket):
        """Remove a WebSocket client"""
        if client in self.websocket_clients:
            self.websocket_clients.remove(client)
    
    def get_websocket_clients(self) -> List[WebSocket]:
        """Get all WebSocket clients"""
        return self.websocket_clients.copy()

