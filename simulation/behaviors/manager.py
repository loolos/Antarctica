"""
Behavior manager - coordinates behavior transitions and execution.
"""
from typing import Dict, Optional, Tuple
from .base import Behavior, BehaviorContext
from .idle import IdleBehavior
from .searching import SearchingBehavior
from .targeting import TargetingBehavior
from .fleeing import FleeingBehavior
from .social import SocialBehavior
from ..animals import Animal, Penguin, Seal, Fish
from ..config import get_config


class BehaviorManager:
    """
    Manages animal behaviors using Strategy pattern.
    
    This class coordinates behavior transitions based on animal state,
    energy levels, and environmental conditions. It follows a priority
    system: fleeing > targeting > social > searching > idle.
    """
    
    def __init__(self):
        """Initialize behavior manager with all behavior strategies."""
        self.behaviors: Dict[str, Behavior] = {
            'idle': IdleBehavior(),
            'searching': SearchingBehavior(),
            'targeting': TargetingBehavior(),
            'fleeing': FleeingBehavior(),
            'social': SocialBehavior(),
        }
    
    def get_behavior(self, state: str) -> Optional[Behavior]:
        """
        Get behavior strategy for a given state.
        
        Args:
            state: Behavior state name
            
        Returns:
            Behavior instance or None if state not found
        """
        return self.behaviors.get(state)
    
    def determine_behavior(
        self, 
        context: BehaviorContext,
        current_state: str
    ) -> str:
        """
        Determine the appropriate behavior state based on context.
        
        Priority order: fleeing > targeting > social > searching > idle
        
        Args:
            context: Behavior context
            current_state: Current behavior state
            
        Returns:
            str: New behavior state name
        """
        animal = context.animal
        config = get_config()
        energy_percent = animal.energy / animal.max_energy
        
        # Priority 1: Fleeing (highest priority)
        if isinstance(animal, Penguin):
            fleeing_behavior = self.behaviors['fleeing']
            if fleeing_behavior.can_transition_to(context) or current_state == 'fleeing':
                if current_state != 'fleeing':
                    fleeing_behavior.on_enter(context)
                return 'fleeing'
        
        # Priority 2: Targeting (if already targeting, continue)
        if current_state == 'targeting':
            return 'targeting'
        
        # Priority 3: Social (when energy > 90%)
        if isinstance(animal, (Penguin, Seal)) and energy_percent > config.ENERGY_THRESHOLD_HIGH:
            social_behavior = self.behaviors['social']
            if social_behavior.can_transition_to(context):
                if current_state != 'social':
                    social_behavior.on_enter(context)
                return 'social'
        
        # Priority 4: Searching (when energy < 60% and not in cooldown)
        if isinstance(animal, (Penguin, Seal)):
            if (energy_percent < config.ENERGY_THRESHOLD_HUNTING and
                energy_percent <= config.ENERGY_THRESHOLD_HIGH and
                animal.hunting_cooldown == 0):
                searching_behavior = self.behaviors['searching']
                if searching_behavior.can_transition_to(context):
                    if current_state != 'searching':
                        searching_behavior.on_enter(context)
                    return 'searching'
        
        # Priority 5: Idle (default)
        return 'idle'
    
    def execute_behavior(
        self,
        context: BehaviorContext,
        state: str
    ) -> Tuple[float, float]:
        """
        Execute behavior and return movement vector.
        
        Args:
            context: Behavior context
            state: Current behavior state
            
        Returns:
            Tuple[float, float]: (dx, dy) movement vector
        """
        behavior = self.get_behavior(state)
        if behavior:
            return behavior.execute(context)
        return 0.0, 0.0

