"""
Fleeing behavior - animal is fleeing from a predator.
"""
from typing import Tuple
import random
import math
from .base import Behavior, BehaviorContext
from ..config import get_config
from ..animals import Penguin


class FleeingBehavior(Behavior):
    """
    Fleeing behavior - animal flees from a predator.
    
    The animal moves away from the predator in a fixed direction
    for a set duration (3 seconds), with some random variation.
    """
    
    def execute(self, context: BehaviorContext) -> Tuple[float, float]:
        """
        Execute fleeing behavior - move away from predator.
        
        Returns:
            Tuple[float, float]: Movement vector away from predator
        """
        config = get_config()
        animal = context.animal
        
        if animal.flee_cooldown > 0:
            # Still fleeing: continue in fixed direction
            animal.flee_cooldown -= 1
            
            # Move in the fixed fleeing direction
            flee_distance = config.FLEE_DISTANCE_MIN + random.uniform(
                0, 
                config.FLEE_DISTANCE_MAX - config.FLEE_DISTANCE_MIN
            )
            dx = math.cos(animal.flee_edge_direction) * flee_distance
            dy = math.sin(animal.flee_edge_direction) * flee_distance
            
            # Apply boundary constraint
            dx, dy = context.engine._constrain_direction_near_edge(animal, dx, dy)
            
            return dx, dy
        else:
            # Cooldown expired, will transition to other state
            return 0, 0
    
    def can_transition_to(self, context: BehaviorContext) -> bool:
        """
        Can transition to fleeing when a predator is detected.
        
        Returns:
            bool: True if predator is nearby
        """
        # Only penguins flee from seals
        if not isinstance(context.animal, Penguin):
            return False
        
        # Check for nearby predators
        config = get_config()
        is_on_land = context.is_on_land
        
        # Perception range depends on location
        if is_on_land:
            perception_range = config.PENGUIN_PERCEPTION_LAND
        else:
            perception_range = config.PENGUIN_PERCEPTION_SEA
        
        from ..animals import Seal
        predators = context.get_nearby_animals(Seal, perception_range)
        
        return len(predators) > 0
    
    def on_enter(self, context: BehaviorContext):
        """
        Initialize fleeing direction when entering flee state.
        
        Calculates direction away from nearest predator with random variation,
        and applies boundary constraints.
        """
        config = get_config()
        animal = context.animal
        engine = context.engine
        
        # Find nearest predator
        is_on_land = context.is_on_land
        if is_on_land:
            perception_range = config.PENGUIN_PERCEPTION_LAND
        else:
            perception_range = config.PENGUIN_PERCEPTION_SEA
        
        predators = [s for s in engine.world.seals if s.is_alive()]
        nearest_predator = engine._find_nearest(animal, predators, max_distance=perception_range)
        
        if nearest_predator:
            # Calculate base fleeing direction (away from predator)
            base_dx = animal.x - nearest_predator.x
            base_dy = animal.y - nearest_predator.y
            base_flee_angle = math.atan2(base_dy, base_dx) if (base_dx != 0 or base_dy != 0) else random.uniform(0, 2 * math.pi)
            
            # Add random variation to fleeing direction (±45 degrees)
            angle_variation = random.uniform(-config.FLEE_ANGLE_VARIATION, config.FLEE_ANGLE_VARIATION)
            flee_angle = (base_flee_angle + angle_variation) % (2 * math.pi)
            
            # Constrain direction to avoid hitting boundaries
            temp_dx = math.cos(flee_angle) * 100
            temp_dy = math.sin(flee_angle) * 100
            constrained_dx, constrained_dy = engine._constrain_direction_near_edge(animal, temp_dx, temp_dy)
            flee_angle = math.atan2(constrained_dy, constrained_dx)
            
            # Store the fleeing direction (fixed for 3 seconds)
            animal.flee_edge_direction = flee_angle
            animal.flee_cooldown = config.FLEE_COOLDOWN_TICKS

