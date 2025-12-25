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
    ice_coverage: float = 0.8
    temperature: float = -10.0
    sea_level: float = 100.0
    season: int = 0
    ice_floes: list = None  # List of dicts: {'x': float, 'y': float, 'radius': float}

    def __post_init__(self):
        if self.ice_floes is None:
            self.generate_ice_floes()

    def generate_ice_floes(self):
        """Generate random ice floes"""
        import random
        self.ice_floes = []
        # Generate 5-8 random ice islands
        num_floes = random.randint(5, 8)
        for _ in range(num_floes):
            self.ice_floes.append({
                'x': random.uniform(100, self.width - 100),
                'y': random.uniform(100, self.height - 100),
                'radius': random.uniform(30, 80)
            })

    def is_land(self, x: float, y: float) -> bool:
        """Check if position is land (on any ice floe)"""
        if not self.ice_floes:
            return False
            
        for floe in self.ice_floes:
            dx = x - floe['x']
            dy = y - floe['y']
            if dx*dx + dy*dy <= floe['radius']**2:
                return True
        return False
    
    def is_sea(self, x: float, y: float) -> bool:
        """Check if position is sea"""
        return not self.is_land(x, y)
    
    def get_ice_thickness(self, x: float, y: float) -> float:
        """Get ice thickness at position"""
        if self.is_land(x, y):
            return 2.0 # Land is thick ice
            
        if self.temperature < -5:
            return min(1.0, abs(self.temperature) / 20.0)
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
        
        # Slowly drift ice floes
        for floe in self.ice_floes:
             # Very slow drift
            floe['x'] += 0.01 
            if floe['x'] > self.width:
                floe['x'] = 0


