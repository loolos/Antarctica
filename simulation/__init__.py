"""
Antarctic ecosystem simulation core
"""

from .engine import SimulationEngine
from .world import WorldState
from .animals import Penguin, Seal, Fish
from .environment import Environment

__all__ = [
    'SimulationEngine',
    'WorldState',
    'Penguin',
    'Seal',
    'Fish',
    'Environment',
]

