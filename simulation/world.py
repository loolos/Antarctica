"""
World state definition
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any
from .animals import Penguin, Seal, Fish
from .environment import Environment


@dataclass
class WorldState:
    """World state"""
    tick: int = 0
    penguins: List[Penguin] = field(default_factory=list)
    seals: List[Seal] = field(default_factory=list)
    fish: List[Fish] = field(default_factory=list)
    environment: Environment = field(default_factory=Environment)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (for JSON serialization)"""
        return {
            "tick": self.tick,
            "penguins": [
                {
                    "id": p.id,
                    "x": p.x,
                    "y": p.y,
                    "energy": p.energy,
                    "age": p.age,
                    "state": p.state,
                    "max_energy": p.max_energy,
                }
                for p in self.penguins
            ],
            "seals": [
                {
                    "id": s.id,
                    "x": s.x,
                    "y": s.y,
                    "energy": s.energy,
                    "age": s.age,
                    "state": s.state,
                    "max_energy": s.max_energy,
                }
                for s in self.seals
            ],
            "fish": [
                {
                    "id": f.id,
                    "x": f.x,
                    "y": f.y,
                    "energy": f.energy,
                    "age": f.age,
                    "max_energy": f.max_energy,
                }
                for f in self.fish
            ],
            "environment": {
                "width": self.environment.width,
                "height": self.environment.height,
                "ice_coverage": self.environment.ice_coverage,
                "temperature": self.environment.temperature,
                "sea_level": self.environment.sea_level,
                "season": self.environment.season,
                "ice_floes": self.environment.ice_floes,
            }
        }
    
    def get_animal_count(self) -> Dict[str, int]:
        """Get count of each animal type"""
        return {
            "penguins": len(self.penguins),
            "seals": len(self.seals),
            "fish": len(self.fish),
        }

