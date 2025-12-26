"""
Targeting behavior - animal is actively pursuing a locked-on target.
"""
from typing import Tuple, Optional
import math
from .base import Behavior, BehaviorContext
from ..config import get_config
from ..animals import Penguin, Seal, Fish


class TargetingBehavior(Behavior):
    """
    Targeting behavior - animal is actively pursuing a specific target.
    
    The animal moves directly toward a locked-on target (prey).
    If the target is too far or lost, transitions back to searching.
    """
    
    def execute(self, context: BehaviorContext) -> Tuple[float, float]:
        """
        Execute targeting behavior - move toward target.
        
        Returns:
            Tuple[float, float]: Movement vector toward target
        """
        animal = context.animal
        
        # Find the target by ID
        target = self._find_target(context)
        
        if not target:
            # Target lost, will transition to searching
            return 0, 0
        
        # Move toward target
        dx = target.x - animal.x
        dy = target.y - animal.y
        
        return dx, dy
    
    def _find_target(self, context: BehaviorContext) -> Optional[Animal]:
        """Find the target animal by ID."""
        animal = context.animal
        
        if not animal.target_id:
            return None
        
        # Search in all animal lists
        for target in context.engine.world.penguins + context.engine.world.seals + context.engine.world.fish:
            if target.id == animal.target_id and target.is_alive():
                return target
        
        return None
    
    def can_transition_to(self, context: BehaviorContext) -> bool:
        """
        Can transition to targeting when a valid target is found.
        
        Returns:
            bool: True if animal can target
        """
        # Transition is handled by engine when target is found
        return False
    
    def on_enter(self, context: BehaviorContext):
        """Called when entering targeting state."""
        pass
    
    def on_exit(self, context: BehaviorContext):
        """Clear target when exiting targeting state."""
        context.animal.target_id = ""

