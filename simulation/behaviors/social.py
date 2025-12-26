"""
Social behavior - animal seeks social interaction (e.g., on ice floes).
"""
from typing import Tuple
import random
import math
from .base import Behavior, BehaviorContext
from ..config import get_config
from ..animals import Penguin, Seal


class SocialBehavior(Behavior):
    """
    Social behavior - animal seeks social interaction.
    
    When energy is high (>90%), animals seek ice floes for socializing
    instead of hunting.
    """
    
    def execute(self, context: BehaviorContext) -> Tuple[float, float]:
        """
        Execute social behavior - move toward nearest ice floe.
        
        Returns:
            Tuple[float, float]: Movement vector toward ice floe
        """
        animal = context.animal
        engine = context.engine
        
        # Find nearest ice floe
        nearest_floe = None
        min_dist = float('inf')
        
        for floe in engine.world.environment.ice_floes:
            dx = floe['x'] - animal.x
            dy = floe['y'] - animal.y
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist < min_dist:
                min_dist = dist
                nearest_floe = floe
        
        if nearest_floe:
            # Move toward ice floe center
            dx = nearest_floe['x'] - animal.x
            dy = nearest_floe['y'] - animal.y
            return dx, dy
        
        # No ice floe found, small random movement
        return random.uniform(-10, 10), random.uniform(-10, 10)
    
    def can_transition_to(self, context: BehaviorContext) -> bool:
        """
        Can transition to social when energy is very high.
        
        Returns:
            bool: True if animal should socialize
        """
        if not isinstance(context.animal, (Penguin, Seal)):
            return False
        
        config = get_config()
        energy_percent = context.animal.energy / context.animal.max_energy
        
        # Socialize when energy > 90%
        return energy_percent > config.ENERGY_THRESHOLD_HIGH

