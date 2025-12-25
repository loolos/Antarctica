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
        
        # Handle spontaneous generation
        self._handle_spawning()
        
        # Remove dead animals
        self._remove_dead_animals()
    
    def _handle_spawning(self):
        """Handle spontaneous generation of animals"""
        # Ensure minimum fish population
        if len(self.world.fish) < 20:
            if random.random() < 0.1: # 10% chance per tick to spawn a fish if low
                self.world.fish.append(
                    Fish(
                        id=f"fish_spawn_{self.world.tick}_{random.randint(100,999)}",
                        x=random.uniform(0, self.world.environment.width),
                        y=random.uniform(0, self.world.environment.height),
                        energy=random.uniform(20, 40)
                    )
                )
    
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
        """Move animal with physics and AI"""
        # 1. Determine current terrain
        is_on_land = self.world.environment.is_land(animal.x, animal.y)
        
        # Update animal state based on actual location
        if is_on_land:
            animal.state = "land"
            speed = animal.land_speed
        else:
            animal.state = "sea"
            speed = animal.water_speed
            
        # 2. AI Decision Making
        dx, dy = 0, 0
        target = None
        
        # Priorities:
        # 1. Breeding/Resting (if needed and not on land)
        needs_land = False
        if isinstance(animal, (Penguin, Seal)):
            if animal.breeding_cooldown == 0 and animal.energy > animal.max_energy * 0.8:
                needs_land = True # Go to land to breed
            elif animal.energy < animal.max_energy * 0.3:
                needs_land = True # Go to land to rest
        
        if needs_land and not is_on_land:
            # Find nearest ice floe center
            floes = self.world.environment.ice_floes
            if floes:
                nearest_floe = min(floes, key=lambda f: (f['x']-animal.x)**2 + (f['y']-animal.y)**2)
                # Move towards it
                dx = nearest_floe['x'] - animal.x
                dy = nearest_floe['y'] - animal.y
        
        # 2. Safety (Avoid Predators) - High Priority override
        # Penguins should flee from Seals
        if isinstance(animal, Penguin):
            predators = [s for s in self.world.seals if s.is_alive()]
            nearest_predator = self._find_nearest(animal, predators, max_distance=150) # Perception range
            
            if nearest_predator:
                # Flee!
                dx = animal.x - nearest_predator.x
                dy = animal.y - nearest_predator.y
                # If on land, flee less frantically? No, run for your life regardless.
                # If in water, this effectively makes them swim away.
                target = nearest_predator # Just to mark as "busy" so we don't hunt while fleeing
        
        # 3. Hunting (if hungry and in water, or Seal on land hunting Penguin)
        if not target and (animal.energy < animal.max_energy * 0.9):
            prey_type = None
            if isinstance(animal, Penguin) and animal.state == "sea":
                prey_type = Fish
            elif isinstance(animal, Seal):
                # Seals hunt Penguins everywhere (prioritized) or Fish in sea
                prey_type = (Penguin, Fish) if animal.state == "sea" else Penguin
            
            if prey_type:
                # Find prey (Global range for stronger AI)
                potential_prey = []
                if isinstance(prey_type, tuple):
                    for t in prey_type:
                        if t == Penguin: potential_prey.extend(self.world.penguins)
                        if t == Fish: potential_prey.extend(self.world.fish)
                elif prey_type == Penguin:
                    potential_prey = self.world.penguins
                elif prey_type == Fish:
                    potential_prey = self.world.fish
                
                # Filter valid prey
                valid_prey = [
                    p for p in potential_prey 
                    if p.is_alive() and p != animal and 
                    (isinstance(p, Fish) or p.state == animal.state) # Hunt in same medium
                ]
                
                target = self._find_nearest(animal, valid_prey, max_distance=300)
                if target:
                    dx = target.x - animal.x
                    dy = target.y - animal.y
        
        # 3. Wandering (if no other drive)
        if dx == 0 and dy == 0:
            # Smooth random movement
            dx = random.uniform(-10, 10)
            dy = random.uniform(-10, 10)
            
            # Fish avoidance of land (simple bouncing)
            if isinstance(animal, Fish):
                # If near land, swim away
                for floe in self.world.environment.ice_floes:
                    dist_sq = (animal.x - floe['x'])**2 + (animal.y - floe['y'])**2
                    if dist_sq < (floe['radius'] + 20)**2:
                        # Swim away from center
                        dx = animal.x - floe['x']
                        dy = animal.y - floe['y']
        
        # Normalize and apply speed
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            dx = (dx / dist) * speed
            dy = (dy / dist) * speed
        
        # Apply movement
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

