"""
Simulation engine
"""
import random
import math
from typing import List
from .world import WorldState
from .animals import Penguin, Seal, Fish
from .environment import Environment


class SimulationEngine:
    """Simulation engine core"""
    
    def __init__(self, width: int = 800, height: int = 600):
        self.world = WorldState()
        self.world.environment = Environment(width=width, height=height)
        self._initialize_world()
    
    def _initialize_world(self):
        """Initialize the world"""
        # Create initial penguins (on land)
        for i in range(10):
            self.world.penguins.append(
                Penguin(
                    id=f"penguin_{i}",
                    x=random.uniform(0, self.world.environment.width * 0.3),
                    y=random.uniform(0, self.world.environment.height),
                    energy=random.uniform(50, 100),
                    state="land"
                )
            )
        
        # Create initial seals (in the sea)
        for i in range(5):
            self.world.seals.append(
                Seal(
                    id=f"seal_{i}",
                    x=random.uniform(self.world.environment.width * 0.5, self.world.environment.width),
                    y=random.uniform(0, self.world.environment.height),
                    energy=random.uniform(80, 150),
                    state="sea"
                )
            )
        
        # Create initial fish (in the sea)
        for i in range(50):
            self.world.fish.append(
                Fish(
                    id=f"fish_{i}",
                    x=random.uniform(self.world.environment.width * 0.3, self.world.environment.width),
                    y=random.uniform(0, self.world.environment.height),
                    energy=random.uniform(20, 40),
                )
            )
    
    def tick(self):
        """Execute one time step"""
        self.world.tick += 1
        
        # Update environment
        self.world.environment.tick()
        
        # Update all animals
        self._update_animals()
        
        # Handle predation
        self._handle_predation()
        
        # Handle breeding
        self._handle_breeding()
        
        # Remove dead animals
        self._remove_dead_animals()
    
    def _update_animals(self):
        """Update all animals' states"""
        # Update penguins
        for penguin in self.world.penguins:
            penguin.tick()
            self._move_animal(penguin)
        
        # Update seals
        for seal in self.world.seals:
            seal.tick()
            self._move_animal(seal)
        
        # Update fish
        for fish in self.world.fish:
            fish.tick()
            self._move_animal(fish)
    
    def _move_animal(self, animal):
        """Move animal"""
        if isinstance(animal, Fish):
            # Fish swim randomly
            dx = random.uniform(-animal.speed, animal.speed)
            dy = random.uniform(-animal.speed, animal.speed)
            animal.move(dx, dy, self.world.environment.width, self.world.environment.height)
        
        elif isinstance(animal, Penguin):
            # Penguins: random movement on land, search for fish in sea
            if animal.state == "land":
                dx = random.uniform(-2, 2)
                dy = random.uniform(-2, 2)
            else:  # sea
                # Find nearest fish
                nearest_fish = self._find_nearest(animal, self.world.fish, max_distance=50)
                if nearest_fish:
                    dx = (nearest_fish.x - animal.x) * 0.1
                    dy = (nearest_fish.y - animal.y) * 0.1
                else:
                    dx = random.uniform(-1, 1)
                    dy = random.uniform(-1, 1)
            animal.move(dx, dy, self.world.environment.width, self.world.environment.height)
        
        elif isinstance(animal, Seal):
            # Seals: hunt penguins or fish
            if animal.state == "sea":
                # Prioritize hunting penguins
                nearest_penguin = self._find_nearest(animal, self.world.penguins, max_distance=80)
                if nearest_penguin and nearest_penguin.state == "sea":
                    dx = (nearest_penguin.x - animal.x) * 0.08
                    dy = (nearest_penguin.y - animal.y) * 0.08
                else:
                    # Hunt fish
                    nearest_fish = self._find_nearest(animal, self.world.fish, max_distance=60)
                    if nearest_fish:
                        dx = (nearest_fish.x - animal.x) * 0.1
                        dy = (nearest_fish.y - animal.y) * 0.1
                    else:
                        dx = random.uniform(-1, 1)
                        dy = random.uniform(-1, 1)
            else:  # land
                dx = random.uniform(-1, 1)
                dy = random.uniform(-1, 1)
            animal.move(dx, dy, self.world.environment.width, self.world.environment.height)
    
    def _find_nearest(self, animal, targets: List, max_distance: float = float('inf')):
        """Find nearest target"""
        nearest = None
        min_dist = max_distance
        
        for target in targets:
            if not target.is_alive():
                continue
            dist = animal.distance_to(target)
            if dist < min_dist:
                min_dist = dist
                nearest = target
        
        return nearest
    
    def _handle_predation(self):
        """Handle predation"""
        # Seals eat penguins (in the sea)
        for seal in self.world.seals[:]:
            if seal.state != "sea" or not seal.is_alive():
                continue
            
            for penguin in self.world.penguins[:]:
                if penguin.state != "sea" or not penguin.is_alive():
                    continue
                
                if seal.distance_to(penguin) < 10:
                    # Predation successful
                    seal.gain_energy(40)
                    self.world.penguins.remove(penguin)
                    break
        
        # Seals eat fish
        for seal in self.world.seals[:]:
            if seal.state != "sea" or not seal.is_alive():
                continue
            
            for fish in self.world.fish[:]:
                if not fish.is_alive():
                    continue
                
                if seal.distance_to(fish) < 8:
                    # Predation successful
                    seal.gain_energy(20)
                    self.world.fish.remove(fish)
                    break
        
        # Penguins eat fish (in the sea)
        for penguin in self.world.penguins[:]:
            if penguin.state != "sea" or not penguin.is_alive():
                continue
            
            for fish in self.world.fish[:]:
                if not fish.is_alive():
                    continue
                
                if penguin.distance_to(fish) < 5:
                    # Predation successful
                    penguin.gain_energy(15)
                    self.world.fish.remove(fish)
                    break
    
    def _handle_breeding(self):
        """Handle breeding"""
        # Penguins breed (on land)
        breeding_penguins = [p for p in self.world.penguins if p.can_breed() and p.state == "land"]
        if len(breeding_penguins) >= 2:
            # Random pairing
            random.shuffle(breeding_penguins)
            for i in range(0, len(breeding_penguins) - 1, 2):
                p1, p2 = breeding_penguins[i], breeding_penguins[i + 1]
                if p1.distance_to(p2) < 20:
                    # Breeding successful
                    baby = p1.breed()
                    p2.breeding_cooldown = p2.max_breeding_cooldown
                    p2.consume_energy(30)
                    self.world.penguins.append(baby)
        
        # Seals breed (on land)
        breeding_seals = [s for s in self.world.seals if s.can_breed() and s.state == "land"]
        if len(breeding_seals) >= 2:
            random.shuffle(breeding_seals)
            for i in range(0, len(breeding_seals) - 1, 2):
                s1, s2 = breeding_seals[i], breeding_seals[i + 1]
                if s1.distance_to(s2) < 25:
                    baby = s1.breed()
                    s2.breeding_cooldown = s2.max_breeding_cooldown
                    s2.consume_energy(50)
                    self.world.seals.append(baby)
        
        # Fish breed (in the sea)
        breeding_fish = [f for f in self.world.fish if f.is_alive() and f.energy > 30]
        if len(breeding_fish) >= 2 and random.random() < 0.1:  # 10% breeding probability
            random.shuffle(breeding_fish)
            for i in range(0, min(5, len(breeding_fish) - 1), 2):  # Max 5 pairs
                f1, f2 = breeding_fish[i], breeding_fish[i + 1]
                if f1.distance_to(f2) < 10:
                    baby = f1.breed()
                    f1.consume_energy(10)
                    f2.consume_energy(10)
                    self.world.fish.append(baby)
    
    def _remove_dead_animals(self):
        """Remove dead animals"""
        self.world.penguins = [p for p in self.world.penguins if p.is_alive()]
        self.world.seals = [s for s in self.world.seals if s.is_alive()]
        self.world.fish = [f for f in self.world.fish if f.is_alive()]
    
    def get_state(self) -> WorldState:
        """Get current world state"""
        return self.world
    
    def step(self, n: int = 1):
        """Advance N steps"""
        for _ in range(n):
            self.tick()

