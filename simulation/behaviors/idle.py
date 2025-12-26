"""
Idle behavior - animal is resting or wandering without specific goal.
"""
from typing import Tuple
import random
import math
from .base import Behavior, BehaviorContext
from ..config import get_config


class IdleBehavior(Behavior):
    """
    Idle behavior - animal wanders randomly or stays still.
    
    This is the default behavior when the animal has no specific goal.
    Animals may wander in small random movements or stay in place.
    """
    
    def execute(self, context: BehaviorContext) -> Tuple[float, float]:
        """
        Execute idle behavior - small random movements.
        
        Returns:
            Tuple[float, float]: Small random movement vector
        """
        # Small random wandering
        dx = random.uniform(-5, 5)
        dy = random.uniform(-5, 5)
        return dx, dy
    
    def can_transition_to(self, context: BehaviorContext) -> bool:
        """
        Can transition to idle from any state when energy is sufficient.
        
        Returns:
            bool: True if animal can be idle
        """
        # Can always be idle (default state)
        return True

