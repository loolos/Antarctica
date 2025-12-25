"""
Animal class definitions
"""
from typing import Literal
from dataclasses import dataclass, field
import random
import math


@dataclass
class Animal:
    """Base animal class"""
    id: str
    x: float
    y: float
    energy: float
    age: int = 0
    max_energy: float = 100.0
    max_age: int = 1000
    land_speed: float = 1.0
    water_speed: float = 1.0
    
    def move(self, dx: float, dy: float, world_width: int, world_height: int):
        """Move the animal"""
        self.x = max(0, min(world_width - 1, self.x + dx))
        self.y = max(0, min(world_height - 1, self.y + dy))
        self.energy -= 0.1  # Movement consumes energy
    
    def consume_energy(self, amount: float):
        """Consume energy"""
        self.energy = max(0, self.energy - amount)
    
    def gain_energy(self, amount: float):
        """Gain energy"""
        self.energy = min(self.max_energy, self.energy + amount)
    
    def is_alive(self) -> bool:
        """Check if alive"""
        return self.energy > 0 and self.age < self.max_age
    
    def distance_to(self, other: 'Animal') -> float:
        """Calculate distance to another animal"""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
    
    def tick(self):
        """Update each tick"""
        self.age += 1
        self.consume_energy(0.05)  # Basal metabolic rate


@dataclass
class Penguin(Animal):
    """Penguin"""
    state: Literal["land", "sea"] = "land"
    breeding_cooldown: int = 0
    max_breeding_cooldown: int = 200
    
    def __post_init__(self):
        self.max_energy = 150.0
        self.max_age = 800
        self.land_speed = 2.0  # Agile on land
        self.water_speed = 4.0  # Fast in water
    
    def can_breed(self) -> bool:
        """检查是否可以繁殖"""
        return (self.breeding_cooldown == 0 and 
                self.energy > 80 and 
                self.state == "land")
    
    def breed(self) -> 'Penguin':
        """繁殖"""
        self.breeding_cooldown = self.max_breeding_cooldown
        self.consume_energy(30)
        return Penguin(
            id=f"penguin_{random.randint(10000, 99999)}",
            x=self.x + random.uniform(-5, 5),
            y=self.y + random.uniform(-5, 5),
            energy=50.0
        )
    
    def tick(self):
        """Penguin behavior each tick"""
        super().tick()
        if self.breeding_cooldown > 0:
            self.breeding_cooldown -= 1
        
        # State transitions handled by engine based on location
        

@dataclass
class Seal(Animal):
    """Seal"""
    state: Literal["land", "sea"] = "sea"
    breeding_cooldown: int = 0
    max_breeding_cooldown: int = 300
    
    def __post_init__(self):
        self.max_energy = 200.0
        self.max_age = 1200
        self.land_speed = 0.5   # Clumsy on land
        self.water_speed = 5.5  # Very fast in water
    
    def can_breed(self) -> bool:
        """Check if can breed"""
        return (self.breeding_cooldown == 0 and 
                self.energy > 100 and 
                self.state == "land")
    
    def breed(self) -> 'Seal':
        """Breed"""
        self.breeding_cooldown = self.max_breeding_cooldown
        self.consume_energy(50)
        return Seal(
            id=f"seal_{random.randint(10000, 99999)}",
            x=self.x + random.uniform(-5, 5),
            y=self.y + random.uniform(-5, 5),
            energy=80.0
        )
    
    def tick(self):
        """Seal behavior each tick"""
        super().tick()
        if self.breeding_cooldown > 0:
            self.breeding_cooldown -= 1


@dataclass
class Fish(Animal):
    """Fish"""
    speed: float = 1.0  # Deprecated, use water_speed
    
    def __post_init__(self):
        self.max_energy = 50.0
        self.max_age = 500
        self.water_speed = 3.0
        self.land_speed = 0.0 # Cannot move on land
    
    def tick(self):
        """Fish behavior each tick"""
        super().tick()
        # Fish swim randomly
        if random.random() < 0.3:
            dx = random.uniform(-self.speed, self.speed)
            dy = random.uniform(-self.speed, self.speed)
            # Note: World dimensions needed here, movement handled by engine
    
    def breed(self) -> 'Fish':
        """Breed"""
        return Fish(
            id=f"fish_{random.randint(10000, 99999)}",
            x=self.x + random.uniform(-3, 3),
            y=self.y + random.uniform(-3, 3),
            energy=25.0
        )

