"""
Environment class definition
"""
from dataclasses import dataclass
from typing import Tuple


@dataclass
class Environment:
    """Environment state"""
    width: int = 800
    height: int = 600
    ice_coverage: float = 0.8  # Ice coverage 0-1
    temperature: float = -10.0  # Temperature in Celsius
    sea_level: float = 100.0  # Sea level height
    season: int = 0  # Season (0-3: Spring, Summer, Autumn, Winter)
    
    def is_land(self, x: float, y: float) -> bool:
        """Check if position is land"""
        # Simplified: left side is land, right side is sea
        # Can be calculated more complexly based on ice_coverage
        land_threshold = self.width * (1 - self.ice_coverage)
        return x < land_threshold
    
    def is_sea(self, x: float, y: float) -> bool:
        """Check if position is sea"""
        return not self.is_land(x, y)
    
    def get_ice_thickness(self, x: float, y: float) -> float:
        """Get ice thickness at position"""
        if self.is_sea(x, y):
            # Sea area, calculate ice thickness based on temperature
            if self.temperature < -5:
                return min(1.0, abs(self.temperature) / 20.0)
            return 0.0
        return 0.0
    
    def tick(self):
        """Update environment each tick"""
        # Season change (1000 ticks per season cycle)
        self.season = (self.season + 1) % 4000
        
        # Adjust temperature based on season
        season_factor = self.season / 1000.0
        if season_factor < 1:  # Spring
            self.temperature = -5 + season_factor * 5
        elif season_factor < 2:  # Summer
            self.temperature = 0 + (season_factor - 1) * 5
        elif season_factor < 3:  # Autumn
            self.temperature = 5 - (season_factor - 2) * 5
        else:  # Winter
            self.temperature = 0 - (season_factor - 3) * 10
        
        # Temperature affects ice coverage
        if self.temperature > 0:
            self.ice_coverage = max(0.3, self.ice_coverage - 0.001)
        else:
            self.ice_coverage = min(0.9, self.ice_coverage + 0.001)

