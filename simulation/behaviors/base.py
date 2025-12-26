"""
Base behavior classes for Strategy pattern.
"""
from abc import ABC, abstractmethod
from typing import Optional, Tuple
from dataclasses import dataclass
from ..animals import Animal


@dataclass
class BehaviorContext:
    """
    Context information passed to behavior strategies.
    
    This contains all the information a behavior needs to make decisions,
    avoiding tight coupling between behaviors and the engine.
    """
    engine: 'SimulationEngine'  # Forward reference
    animal: Animal
    is_on_land: bool
    world_width: int
    world_height: int
    
    def get_nearby_animals(
        self, 
        animal_type: type, 
        max_distance: float,
        filter_func: Optional[callable] = None
    ) -> list:
        """Get nearby animals of a specific type"""
        if animal_type is None:
            return []
        
        # Get appropriate list from world
        from ..animals import Penguin, Seal, Fish
        if animal_type == Penguin:
            candidates = self.engine.world.penguins
        elif animal_type == Seal:
            candidates = self.engine.world.seals
        elif animal_type == Fish:
            candidates = self.engine.world.fish
        else:
            return []
        
        # Use spatial grid for efficient lookup
        nearby = self.engine.spatial_grid.get_nearby_animals(
            self.animal.x,
            self.animal.y,
            max_distance,
            exclude=self.animal,
            filter_func=filter_func
        )
        
        # Filter by type
        return [a for a in nearby if isinstance(a, animal_type) and a.is_alive()]


class Behavior(ABC):
    """
    Base class for animal behaviors using Strategy pattern.
    
    Each behavior implements a specific animal action pattern (idle, searching,
    targeting, fleeing, etc.). This allows for easy extension and modification
    of behaviors without changing the core engine logic.
    """
    
    @abstractmethod
    def execute(self, context: BehaviorContext) -> Tuple[float, float]:
        """
        Execute the behavior and return movement vector.
        
        Args:
            context: Behavior context containing engine, animal, and environment info
            
        Returns:
            Tuple[float, float]: (dx, dy) movement vector
        """
        pass
    
    @abstractmethod
    def can_transition_to(self, context: BehaviorContext) -> bool:
        """
        Check if animal can transition to this behavior.
        
        Args:
            context: Behavior context
            
        Returns:
            bool: True if transition is allowed
        """
        pass
    
    def on_enter(self, context: BehaviorContext):
        """
        Called when animal enters this behavior state.
        
        Override in subclasses to initialize behavior-specific state.
        
        Args:
            context: Behavior context
        """
        pass
    
    def on_exit(self, context: BehaviorContext):
        """
        Called when animal exits this behavior state.
        
        Override in subclasses to clean up behavior-specific state.
        
        Args:
            context: Behavior context
        """
        pass

