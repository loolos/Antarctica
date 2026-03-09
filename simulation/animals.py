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
    # Behavior state tracking
    behavior_state: str = "idle"  # idle, searching, targeting, fleeing, breeding, resting
    hunt_direction_angle: float = 0.0  # Current hunting direction in radians
    hunt_direction_ticks: int = 0  # How long to maintain current direction
    last_x: float = 0.0  # Previous position for boundary detection
    last_y: float = 0.0
    flee_edge_direction: float = 0.0  # Direction along edge when fleeing (in radians)
    target_id: str = ""  # ID of the target being tracked (for distance tracking)
    hunting_cooldown: int = 0  # Cooldown after successful predation (prevents immediate re-hunting)
    flee_cooldown: int = 0  # Cooldown for fleeing state (continues fleeing for 3 seconds after predator is out of sight)
    
    def move(self, dx: float, dy: float, world_width: int, world_height: int):
        """Move the animal"""
        # Store previous position for boundary detection
        self.last_x = self.x
        self.last_y = self.y
        
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Boundary detection - if hitting edge, bounce back
        hit_boundary = False
        if new_x < 0:
            new_x = 0
            hit_boundary = True
        elif new_x >= world_width:
            new_x = world_width - 1
            hit_boundary = True
        if new_y < 0:
            new_y = 0
            hit_boundary = True
        elif new_y >= world_height:
            new_y = world_height - 1
            hit_boundary = True
        
        self.x = new_x
        self.y = new_y
        # Movement consumes energy (from config)
        from .config import get_config
        config = get_config()
        self.energy -= config.ENERGY_CONSUMPTION_MOVE
        
        return hit_boundary  # Return if hit boundary
    
    def consume_energy(self, amount: float):
        """Consume energy"""
        self.energy = max(0, self.energy - amount)
    
    def gain_energy(self, amount: float):
        """Gain energy"""
        self.energy = min(self.max_energy, self.energy + amount)
    
    def is_alive(self) -> bool:
        """Check if alive"""
        # Animals die when energy is depleted or when exceeding max age.
        # Keep age check centralized here so engine cleanup only needs is_alive().
        return self.energy > 0 and self.age < self.max_age
    
    def distance_to(self, other: 'Animal') -> float:
        """Calculate distance to another animal"""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
    
    def is_juvenile(self) -> bool:
        """Check if animal is juvenile (not yet adult)"""
        # Default: juvenile for first 100 ticks (20 seconds at 5 ticks/sec)
        return self.age < 100
    
    def tick(self):
        """Update each tick"""
        self.age += 1
        # Consume energy each tick (basal metabolic rate, from config)
        from .config import get_config
        config = get_config()
        self.consume_energy(config.ENERGY_CONSUMPTION_TICK)


@dataclass
class Penguin(Animal):
    """Penguin"""
    state: Literal["land", "sea"] = "land"
    breeding_cooldown: int = 0
    max_breeding_cooldown: int = 200
    
    def __post_init__(self):
        self.max_energy = 150.0
        self.max_age = 1600
        self.land_speed = 2.0  # Agile on land
        self.water_speed = 4.0  # Fast in water
        self.maturity_age = 100  # Age at which penguin becomes adult (100 ticks = 20 seconds)
    
    def is_juvenile(self) -> bool:
        """Check if penguin is juvenile"""
        return self.age < self.maturity_age
    
    def get_speed(self, is_water: bool) -> float:
        """Get current speed based on age and location"""
        base_speed = self.water_speed if is_water else self.land_speed
        if self.is_juvenile():
            return base_speed * 0.5  # Juveniles move at 50% speed
        return base_speed
    
    def can_breed(self) -> bool:
        """Check if can breed"""
        return (self.breeding_cooldown == 0 and 
                self.energy > 80 and 
                self.state == "land")
    
    def breed(self) -> 'Penguin':
        """Breed and produce offspring"""
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
        if self.hunting_cooldown > 0:
            self.hunting_cooldown -= 1
        if self.flee_cooldown > 0:
            self.flee_cooldown -= 1
        
        # State transitions handled by engine based on location
        

@dataclass
class Seal(Animal):
    """Seal"""
    state: Literal["land", "sea"] = "sea"
    breeding_cooldown: int = 0
    max_breeding_cooldown: int = 300
    
    def __post_init__(self):
        self.max_energy = 200.0
        self.max_age = 2400
        self.land_speed = 0.5   # Clumsy on land
        self.water_speed = 5.5  # Very fast in water
        self.maturity_age = 150  # Age at which seal becomes adult (150 ticks = 30 seconds)
    
    def is_juvenile(self) -> bool:
        """Check if seal is juvenile"""
        return self.age < self.maturity_age
    
    def get_speed(self, is_water: bool) -> float:
        """Get current speed based on age and location"""
        base_speed = self.water_speed if is_water else self.land_speed
        if self.is_juvenile():
            return base_speed * 0.5  # Juveniles move at 50% speed
        return base_speed
    
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
        if self.hunting_cooldown > 0:
            self.hunting_cooldown -= 1


@dataclass
class Seagull(Animal):
    """Seagull - flying or grounded on ice floes. Can hunt fish, socialize when full, flee only when grounded."""
    state: Literal["flying", "grounded"] = "flying"
    breeding_cooldown: int = 0
    max_breeding_cooldown: int = 250
    carrying_fish: bool = False
    prey_processing_ticks: int = 0

    def __post_init__(self):
        self.max_energy = 120.0
        self.max_age = 900
        self.land_speed = 1.5   # On ice (grounded)
        self.water_speed = 6.0  # Flying speed (faster than penguin/seal swimming)
        self.maturity_age = 80

    def is_juvenile(self) -> bool:
        return self.age < self.maturity_age

    def get_speed(self, is_water: bool) -> float:
        # When flying, use water_speed (fast). When grounded, use land_speed.
        base_speed = self.water_speed if self.state == "flying" else self.land_speed
        if self.is_juvenile():
            return base_speed * 0.6
        return base_speed

    def can_breed(self) -> bool:
        """Can breed only when grounded on ice floe (checked by engine)"""
        return (self.breeding_cooldown == 0 and
                self.energy > 90 and
                self.state == "grounded")

    def breed(self) -> 'Seagull':
        """Breed"""
        self.breeding_cooldown = self.max_breeding_cooldown
        self.consume_energy(35)
        return Seagull(
            id=f"seagull_{random.randint(10000, 99999)}",
            x=self.x + random.uniform(-5, 5),
            y=self.y + random.uniform(-5, 5),
            energy=60.0,
            state="grounded"
        )

    def move(self, dx: float, dy: float, world_width: int, world_height: int):
        """Override: flying consumes more energy, extra when carrying fish."""
        from .config import get_config
        config = get_config()
        base_consumption = config.ENERGY_CONSUMPTION_MOVE
        result = super().move(dx, dy, world_width, world_height)
        # Base flying cost is 2x movement energy. Carrying fish costs 1.3x that.
        if self.state == "flying":
            flying_multiplier = 2.0
            if self.carrying_fish:
                flying_multiplier *= config.SEAGULL_CARRYING_ENERGY_MULTIPLIER
            self.consume_energy(base_consumption * (flying_multiplier - 1.0))
        return result

    def tick(self):
        super().tick()
        # Base flying basal cost is 2x. Carrying fish costs 1.3x that.
        if self.state == "flying":
            from .config import get_config
            config = get_config()
            flying_multiplier = 2.0
            if self.carrying_fish:
                flying_multiplier *= config.SEAGULL_CARRYING_ENERGY_MULTIPLIER
            self.consume_energy(config.ENERGY_CONSUMPTION_TICK * (flying_multiplier - 1.0))
        if self.breeding_cooldown > 0:
            self.breeding_cooldown -= 1
        if self.hunting_cooldown > 0:
            self.hunting_cooldown -= 1
        if self.flee_cooldown > 0:
            self.flee_cooldown -= 1


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
