"""
Custom exceptions for simulation
"""


class SimulationError(Exception):
    """Base exception for simulation errors"""
    pass


class AnimalNotFoundError(SimulationError):
    """Raised when an animal is not found"""
    pass


class InvalidConfigurationError(SimulationError):
    """Raised when configuration is invalid"""
    pass


class InvalidStateError(SimulationError):
    """Raised when simulation state is invalid"""
    pass


class BoundaryError(SimulationError):
    """Raised when boundary constraints are violated"""
    pass

