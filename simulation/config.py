"""
Simulation configuration - centralized configuration management
"""
from dataclasses import dataclass
from typing import Tuple


@dataclass
class SimulationConfig:
    """Simulation configuration parameters"""
    
    # World settings
    WORLD_WIDTH: int = 1280
    WORLD_HEIGHT: int = 960
    INITIAL_PENGUINS: int = 10
    INITIAL_SEALS: int = 5
    INITIAL_FISH: int = 50
    INITIAL_SEAGULLS: int = 6
    
    # Penguin settings
    PENGUIN_MAX_ENERGY: float = 150.0
    PENGUIN_MATURITY_AGE: int = 100
    PENGUIN_PERCEPTION_LAND: float = 80.0  # Reduced perception on land (60 + 20)
    PENGUIN_PERCEPTION_SEA: float = 170.0   # Normal perception in sea (150 + 20)
    PENGUIN_ENERGY_RECOVERY_FISH: float = 75.0  # 50% of max energy
    PENGUIN_BASE_SCALE: float = 0.9  # Size scaling for rendering
    
    # Seal settings
    SEAL_MAX_ENERGY: float = 200.0
    SEAL_MATURITY_AGE: int = 150
    SEAL_ENERGY_RECOVERY_FISH: float = 20.0  # 10% of max energy
    
    # Fish settings
    FISH_MAX_ENERGY: float = 40.0
    
    # Seagull settings
    SEAGULL_PREY_SEARCH_RANGE: float = 350.0  # Larger search range for fish (vs 200 for others)
    SEAGULL_ENERGY_RECOVERY_FISH: float = 95.0  # ~79% of max energy - high satisfaction from eating fish
    SEAGULL_FLEE_RANGE_GROUNDED: float = 80.0  # When grounded: flee if penguin/seal within this range
    SEAGULL_HUNTING_DIRECTION_TICKS_MIN: int = 10  # 2 seconds at 5 ticks/sec - fly in one direction
    SEAGULL_HUNTING_DIRECTION_TICKS_MAX: int = 30  # 6 seconds - then random turn (same pattern as penguin/seal, shorter)
    
    # Behavior settings
    FLEE_COOLDOWN_TICKS: int = 15  # 3 seconds at 5 ticks/sec
    HUNTING_COOLDOWN_TICKS: int = 50  # 10 seconds at 5 ticks/sec
    FLEE_DISTANCE_MIN: float = 30.0
    FLEE_DISTANCE_MAX: float = 50.0
    SEARCH_DISTANCE_MIN: float = 30.0
    SEARCH_DISTANCE_MAX: float = 50.0
    FLEE_ANGLE_VARIATION: float = 0.785398  # ±45 degrees (π/4)
    
    # Energy consumption
    ENERGY_CONSUMPTION_MOVE: float = 0.05  # Per movement
    ENERGY_CONSUMPTION_TICK: float = 0.025  # Per tick (basal metabolic rate)
    
    # Energy thresholds
    ENERGY_THRESHOLD_LOW: float = 0.3  # (Unused: no rest on land for penguin/seal)
    ENERGY_THRESHOLD_HUNTING: float = 0.6  # 60% - start hunting
    ENERGY_THRESHOLD_SOCIAL: float = 0.6  # 60% - social behavior
    ENERGY_THRESHOLD_HIGH: float = 0.9  # 90% - no hunting, only socializing
    ENERGY_THRESHOLD_BREEDING: float = 0.8  # 80% - can breed
    
    # Movement settings
    MOVEMENT_SPEED_LAND: float = 1.0
    MOVEMENT_SPEED_WATER: float = 1.0
    JUVENILE_SPEED_MULTIPLIER: float = 0.5  # Juveniles move at 50% speed
    
    # Hunting settings
    HUNTING_DIRECTION_TICKS_MIN: int = 15  # 3 seconds
    HUNTING_DIRECTION_TICKS_MAX: int = 40  # 8 seconds
    MAX_TRACKING_DISTANCE: float = 400.0  # Maximum distance before giving up tracking
    PREY_SEARCH_RANGE: float = 200.0  # Search range for prey
    SEAL_LAND_PENGUIN_HUNT_RANGE: float = 80.0  # Seal on land: hunt penguin only if within this (very close)
    PREY_EXPLORATION_RANGE: float = 600.0  # Exploration range for regular hunting
    SEA_SEARCH_AVOID_FLOE_RANGE: float = 150.0  # In sea searching: if within this of floe center, prefer swimming away
    
    # Boundary settings
    EDGE_MARGIN: float = 50.0  # Consider near edge if within this distance
    
    # Spawning settings
    FISH_SPAWN_RATE: float = 0.25  # Probability per tick when below threshold (25% = ~1.25 fish/sec at 5 ticks/sec)
    FISH_SPAWN_THRESHOLD: int = 50  # Spawn when fish count below this
    MAX_FISH: int = 100
    
    # Breeding settings
    BREEDING_COOLDOWN_TICKS: int = 200  # 40 seconds
    BREEDING_DISTANCE: float = 20.0  # Distance required for breeding
    
    # Age settings
    MAX_AGE: int = 1000
    
    @classmethod
    def get_default(cls) -> 'SimulationConfig':
        """Get default configuration instance"""
        return cls()
    
    def get_energy_threshold(self, threshold_name: str) -> float:
        """Get energy threshold by name"""
        thresholds = {
            'low': self.ENERGY_THRESHOLD_LOW,
            'hunting': self.ENERGY_THRESHOLD_HUNTING,
            'social': self.ENERGY_THRESHOLD_SOCIAL,
            'high': self.ENERGY_THRESHOLD_HIGH,
            'breeding': self.ENERGY_THRESHOLD_BREEDING,
        }
        return thresholds.get(threshold_name.lower(), 0.0)


# Global configuration instance
_config: SimulationConfig = None


def get_config() -> SimulationConfig:
    """Get global configuration instance"""
    global _config
    if _config is None:
        _config = SimulationConfig.get_default()
    return _config


def set_config(config: SimulationConfig):
    """Set global configuration instance"""
    global _config
    _config = config

