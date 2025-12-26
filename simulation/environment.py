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
        """Generate random ice floes with varied sizes and shapes"""
        import random
        import math
        self.ice_floes = []
        # Generate 4-7 random ice islands (fewer but larger)
        num_floes = random.randint(4, 7)
        for _ in range(num_floes):
            # Larger radius range: 60-150 (was 30-80)
            base_radius = random.uniform(60, 150)
            
            # Shape type: 'circle', 'ellipse', or 'irregular'
            shape_type = random.choice(['circle', 'ellipse', 'ellipse', 'irregular'])
            
            if shape_type == 'circle':
                # Simple circle
                self.ice_floes.append({
                    'x': random.uniform(100, self.width - 100),
                    'y': random.uniform(100, self.height - 100),
                    'radius': base_radius,
                    'shape': 'circle',
                    'radius_x': base_radius,
                    'radius_y': base_radius,
                    'rotation': 0
                })
            elif shape_type == 'ellipse':
                # Elliptical shape
                radius_x = base_radius
                radius_y = base_radius * random.uniform(0.6, 1.0)  # Vary aspect ratio
                rotation = random.uniform(0, 2 * math.pi)  # Random rotation
                self.ice_floes.append({
                    'x': random.uniform(100, self.width - 100),
                    'y': random.uniform(100, self.height - 100),
                    'radius': max(radius_x, radius_y),  # Use max for bounding circle
                    'shape': 'ellipse',
                    'radius_x': radius_x,
                    'radius_y': radius_y,
                    'rotation': rotation
                })
            else:  # irregular
                # Irregular shape: use larger radius with variation
                # Create an irregular shape by using a larger base radius
                # and checking distance with some variation
                radius_x = base_radius * random.uniform(0.8, 1.2)
                radius_y = base_radius * random.uniform(0.7, 1.1)
                rotation = random.uniform(0, 2 * math.pi)
                self.ice_floes.append({
                    'x': random.uniform(100, self.width - 100),
                    'y': random.uniform(100, self.height - 100),
                    'radius': max(radius_x, radius_y) * 1.1,  # Slightly larger bounding circle
                    'shape': 'irregular',
                    'radius_x': radius_x,
                    'radius_y': radius_y,
                    'rotation': rotation,
                    'irregularity': random.uniform(0.1, 0.3)  # Amount of irregularity
                })

    def is_land(self, x: float, y: float) -> bool:
        """Check if position is land (on any ice floe)"""
        if not self.ice_floes:
            return False
            
        import math
        for floe in self.ice_floes:
            dx = x - floe['x']
            dy = y - floe['y']
            
            # Quick bounding circle check first
            dist_sq = dx*dx + dy*dy
            if dist_sq > floe['radius']**2:
                continue
            
            # Detailed shape check
            shape = floe.get('shape', 'circle')
            
            if shape == 'circle':
                # Simple circle check
                if dist_sq <= floe['radius']**2:
                    return True
            elif shape == 'ellipse':
                # Ellipse check: rotate point, then check ellipse equation
                rotation = floe.get('rotation', 0)
                radius_x = floe.get('radius_x', floe['radius'])
                radius_y = floe.get('radius_y', floe['radius'])
                
                # Rotate point to ellipse's local coordinate system
                cos_r = math.cos(-rotation)
                sin_r = math.sin(-rotation)
                local_x = dx * cos_r - dy * sin_r
                local_y = dx * sin_r + dy * cos_r
                
                # Check if point is inside ellipse
                if (local_x / radius_x)**2 + (local_y / radius_y)**2 <= 1.0:
                    return True
            elif shape == 'irregular':
                # Irregular shape: use ellipse as base with some variation
                rotation = floe.get('rotation', 0)
                radius_x = floe.get('radius_x', floe['radius'])
                radius_y = floe.get('radius_y', floe['radius'])
                irregularity = floe.get('irregularity', 0.2)
                
                # Rotate point
                cos_r = math.cos(-rotation)
                sin_r = math.sin(-rotation)
                local_x = dx * cos_r - dy * sin_r
                local_y = dx * sin_r + dy * cos_r
                
                # Base ellipse check
                ellipse_value = (local_x / radius_x)**2 + (local_y / radius_y)**2
                
                # Add irregularity based on angle
                angle = math.atan2(local_y, local_x)
                irregular_factor = 1.0 + irregularity * math.sin(angle * 3) * math.cos(angle * 2)
                
                if ellipse_value <= irregular_factor:
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


