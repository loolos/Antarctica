"""
Searching behavior - animal is actively searching for food.
"""
from typing import Tuple, Optional
import random
import math
from .base import Behavior, BehaviorContext
from ..config import get_config
from ..animals import Penguin, Seal, Fish


class SearchingBehavior(Behavior):
    """
    Searching behavior - animal actively searches for prey.
    
    The animal moves in a specific direction for a period of time,
    then changes direction. This creates a search pattern.
    """
    
    def execute(self, context: BehaviorContext) -> Tuple[float, float]:
        """
        Execute searching behavior - move in search direction.
        
        Returns:
            Tuple[float, float]: Movement vector in search direction
        """
        config = get_config()
        animal = context.animal
        
        # Check if we need to set a new searching direction
        if animal.hunt_direction_ticks <= 0:
            # Set new random direction (3-8 seconds = 15-40 ticks at 5 ticks/sec)
            animal.hunt_direction_ticks = random.randint(
                config.HUNTING_DIRECTION_TICKS_MIN, 
                config.HUNTING_DIRECTION_TICKS_MAX
            )
            animal.hunt_direction_angle = random.uniform(0, 2 * math.pi)
        
        # Decrease direction timer
        animal.hunt_direction_ticks -= 1
        
        # Move in the searching direction
        search_distance = config.SEARCH_DISTANCE_MIN + random.uniform(
            0, 
            config.SEARCH_DISTANCE_MAX - config.SEARCH_DISTANCE_MIN
        )
        dx = math.cos(animal.hunt_direction_angle) * search_distance
        dy = math.sin(animal.hunt_direction_angle) * search_distance
        
        return dx, dy
    
    def can_transition_to(self, context: BehaviorContext) -> bool:
        """
        Can transition to searching when energy is low and not in cooldown.
        
        Returns:
            bool: True if animal should start searching
        """
        config = get_config()
        animal = context.animal
        
        if not isinstance(animal, (Penguin, Seal)):
            return False
        
        energy_percent = animal.energy / animal.max_energy
        
        # Can search if:
        # - Energy below hunting threshold
        # - Not in hunting cooldown
        # - Not already fleeing or targeting
        return (
            energy_percent < config.ENERGY_THRESHOLD_HUNTING and
            energy_percent <= config.ENERGY_THRESHOLD_HIGH and
            animal.hunting_cooldown == 0 and
            animal.behavior_state not in ["fleeing", "targeting"]
        )
    
    def on_enter(self, context: BehaviorContext):
        """Initialize searching direction when entering search mode."""
        config = get_config()
        animal = context.animal
        animal.hunt_direction_angle = random.uniform(0, 2 * math.pi)
        animal.hunt_direction_ticks = random.randint(
            config.HUNTING_DIRECTION_TICKS_MIN,
            config.HUNTING_DIRECTION_TICKS_MAX
        )

