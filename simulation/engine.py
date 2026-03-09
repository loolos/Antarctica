"""
Simulation engine - Core simulation logic for Antarctic ecosystem

This module contains the SimulationEngine class, which manages the entire
simulation world including animals, environment, and all interactions.

The engine operates on a tick-based system where each tick represents one
time step in the simulation. During each tick:
- Animals update their behavior and move
- Environment updates (temperature, ice coverage)
- Predation, breeding, and spawning are handled
- Dead animals are removed
"""
import random
import math
from typing import List, Optional, Tuple
from .world import WorldState, FloeFish
from .animals import Penguin, Seal, Fish, Seagull, Animal
from .environment import Environment
from .config import get_config
from .spatial import SpatialGrid


class SimulationEngine:
    """
    Core simulation engine for Antarctic ecosystem simulation.
    
    The SimulationEngine manages the entire simulation world, including:
    - Animal populations (penguins, seals, fish)
    - Environment state (temperature, ice coverage, seasons)
    - Animal behaviors (movement, hunting, fleeing, breeding)
    - Interactions (predation, breeding, spawning)
    
    The engine uses a tick-based system where each tick represents one
    time step. The simulation runs at 5 ticks per second by default.
    
    Attributes:
        world (WorldState): The current state of the simulation world
        
    Example:
        ```python
        engine = SimulationEngine(width=800, height=600)
        engine.step(100)  # Advance 100 ticks
        state = engine.get_state()
        print(f"Tick: {state.tick}, Penguins: {len(state.penguins)}")
        ```
    """
    
    def __init__(self, width: Optional[int] = None, height: Optional[int] = None):
        """
        Initialize the simulation engine.
        
        Args:
            width: World width in pixels (default: from config)
            height: World height in pixels (default: from config)
            
        Note:
            If width/height are not provided, values from SimulationConfig
            will be used (default: 800x600).
        """
        config = get_config()
        # Use config defaults if not provided
        if width is None:
            width = config.WORLD_WIDTH
        if height is None:
            height = config.WORLD_HEIGHT
        self.world = WorldState()
        self.world.environment = Environment(width=width, height=height)
        
        # Initialize spatial grid for efficient neighbor queries
        # Cell size of 100 pixels balances precision and performance
        # This means we check ~9 cells (3x3) for most queries
        self.spatial_grid = SpatialGrid(width, height, cell_size=100.0)
        
        self._initialize_world()
    
    def _initialize_world(self):
        """Initialize the world"""
        config = get_config()
        # Create initial penguins with random positions and ages
        for i in range(config.INITIAL_PENGUINS):
            # Random position anywhere on the map
            x = random.uniform(0, self.world.environment.width)
            y = random.uniform(0, self.world.environment.height)
            
            # Check if position is on land, if not, try to find land position
            if not self.world.environment.is_land(x, y):
                # Try to find a land position (ice floe)
                for attempt in range(20):
                    if self.world.environment.ice_floes:
                        floe = random.choice(self.world.environment.ice_floes)
                        angle = random.uniform(0, 2 * math.pi)
                        distance = random.uniform(0, floe['radius'] * 0.8)
                        x = floe['x'] + math.cos(angle) * distance
                        y = floe['y'] + math.sin(angle) * distance
                        if self.world.environment.is_land(x, y):
                            break
            
            penguin = Penguin(
                id=f"penguin_{i}",
                x=x,
                y=y,
                energy=random.uniform(50, 100),
                state="land" if self.world.environment.is_land(x, y) else "sea"
            )
            # Random age: 0 to 200 ticks (mix of juveniles and adults)
            penguin.age = random.randint(0, 200)
            # Initialize position tracking for boundary detection
            penguin.last_x = penguin.x
            penguin.last_y = penguin.y
            # Initialize cooldowns
            penguin.hunting_cooldown = 0
            penguin.flee_cooldown = 0
            self.world.penguins.append(penguin)
            # Add to spatial grid
            self.spatial_grid.add(penguin)
        
        # Create initial seals with random positions and ages
        for i in range(config.INITIAL_SEALS):
            # Random position anywhere on the map
            x = random.uniform(0, self.world.environment.width)
            y = random.uniform(0, self.world.environment.height)
            
            # Check if position is in sea, if not, try to find sea position
            if self.world.environment.is_land(x, y):
                # Try to find a sea position
                for attempt in range(20):
                    x = random.uniform(0, self.world.environment.width)
                    y = random.uniform(0, self.world.environment.height)
                    if not self.world.environment.is_land(x, y):
                        break
            
            seal = Seal(
                id=f"seal_{i}",
                x=x,
                y=y,
                energy=random.uniform(80, 150),
                state="sea" if not self.world.environment.is_land(x, y) else "land"
            )
            # Random age: 0 to 300 ticks (mix of juveniles and adults)
            seal.age = random.randint(0, 300)
            # Initialize position tracking for boundary detection
            seal.last_x = seal.x
            seal.last_y = seal.y
            # Initialize cooldowns
            seal.hunting_cooldown = 0
            seal.flee_cooldown = 0
            self.world.seals.append(seal)
            # Add to spatial grid
            self.spatial_grid.add(seal)
        
        # Create initial fish (in the sea, not on ice floes)
        for i in range(config.INITIAL_FISH):
            # Find a position in the sea (not on any ice floe)
            x, y = self._find_sea_position()
            fish = Fish(
                id=f"fish_{i}",
                x=x,
                y=y,
                energy=random.uniform(20, 40),
            )
            self.world.fish.append(fish)
            # Add to spatial grid
            self.spatial_grid.add(fish)

        # Create initial seagulls (flying or grounded on ice floe)
        for i in range(config.INITIAL_SEAGULLS):
            x = random.uniform(0, self.world.environment.width)
            y = random.uniform(0, self.world.environment.height)
            initial_state = "grounded" if self.world.environment.is_land(x, y) else "flying"
            seagull = Seagull(
                id=f"seagull_{i}",
                x=x,
                y=y,
                energy=random.uniform(50, 90),
                state=initial_state,
            )
            seagull.age = random.randint(0, 180)
            seagull.last_x = seagull.x
            seagull.last_y = seagull.y
            seagull.breeding_cooldown = 0
            seagull.hunting_cooldown = 0
            seagull.flee_cooldown = 0
            self.world.seagulls.append(seagull)
            self.spatial_grid.add(seagull)
    
    def tick(self):
        """
        Execute one simulation time step (tick).
        
        This method runs the complete simulation logic for one time step:
        1. Increment simulation tick counter
        2. Update environment (temperature, ice coverage, seasons)
        3. Update all animals (movement, behavior, energy consumption)
        4. Handle predation (animals eating other animals)
        5. Handle breeding (animals reproducing)
        6. Handle spontaneous generation (fish spawning)
        7. Remove dead animals
        
        This is the core simulation loop method. It should be called
        repeatedly to advance the simulation.
        """
        self.world.tick += 1
        
        # Update environment
        self.world.environment.tick()

        # Keep spatial index aligned with the latest world lists/positions.
        # This avoids missed nearby-detection when entities were repositioned
        # externally or moved across grid cells in previous ticks.
        self._rebuild_spatial_grid()
        
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
    
    def _find_sea_position(self, max_attempts: int = 50) -> Tuple[float, float]:
        """
        Find a random position in the sea (not on any ice floe).
        
        Attempts to find a valid sea position by randomly sampling positions
        and checking if they are not on land. This is used for spawning fish
        and initializing animals that should start in the sea.
        
        Args:
            max_attempts: Maximum number of random attempts before fallback
            
        Returns:
            Tuple[float, float]: (x, y) coordinates of a sea position
            
        Note:
            If no valid sea position is found after max_attempts, returns
            a fallback position in the right half of the map.
        """
        for _ in range(max_attempts):
            x = random.uniform(0, self.world.environment.width)
            y = random.uniform(0, self.world.environment.height)
            # Check if this position is in the sea (not on land)
            if not self.world.environment.is_land(x, y):
                return x, y
        # If we can't find a sea position after max_attempts, return a position far from ice floes
        # This is a fallback - should rarely happen
        return random.uniform(self.world.environment.width * 0.5, self.world.environment.width), \
               random.uniform(0, self.world.environment.height)
    
    def _handle_spawning(self):
        """Handle spontaneous generation of animals"""
        config = get_config()
        # Ensure minimum fish population - spawn when below threshold
        if len(self.world.fish) < config.FISH_SPAWN_THRESHOLD:
            if random.random() < config.FISH_SPAWN_RATE:
                # Find a position in the sea (not on any ice floe)
                x, y = self._find_sea_position()
                new_fish = Fish(
                    id=f"fish_spawn_{self.world.tick}_{random.randint(100,999)}",
                    x=x,
                    y=y,
                    energy=random.uniform(20, 40)
                )
                self.world.fish.append(new_fish)
                # Add to spatial grid
                self.spatial_grid.add(new_fish)
    
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

        # Update seagulls
        for seagull in self.world.seagulls:
            seagull.tick()
            self._move_animal(seagull)

        # Update fish dropped on ice floes
        for floe_fish in self.world.floe_fish:
            floe_fish.tick()

    def _rebuild_spatial_grid(self):
        """Rebuild spatial index from current world state."""
        self.spatial_grid.clear()
        for animal in self.world.penguins:
            self.spatial_grid.add(animal)
        for animal in self.world.seals:
            self.spatial_grid.add(animal)
        for animal in self.world.fish:
            self.spatial_grid.add(animal)
        for animal in self.world.seagulls:
            self.spatial_grid.add(animal)
    
    def _move_animal(self, animal):
        """Move animal with physics and AI"""
        # 1. Determine current terrain
        is_on_land = self.world.environment.is_land(animal.x, animal.y)
        
        # Update animal state based on actual location (Seagull uses flying/grounded)
        if isinstance(animal, Seagull):
            # Seagull: grounded only when on ice floe; else flying
            if animal.state == "grounded" and not is_on_land:
                animal.state = "flying"  # Drifted off floe
            elif animal.state == "flying" and is_on_land:
                # Could land when arrived at floe (handled in needs_land block)
                pass
        else:
            if is_on_land:
                animal.state = "land"
            else:
                animal.state = "sea"
        
        # Determine speed based on location and age
        if isinstance(animal, (Penguin, Seal, Seagull)):
            # Seagull.get_speed uses its state (flying/grounded), not terrain
            speed = animal.get_speed(not is_on_land)  # True for water, False for land
        else:
            # For fish and other animals, use original logic
            if is_on_land:
                speed = animal.land_speed
            else:
                speed = animal.water_speed
            
        # 2. AI Decision Making
        dx, dy = 0, 0
        target = None
        seagull_processing_locked = False
        
        # Priorities:
        # 1. Breeding/Resting/Social (if needed and not on land)
        needs_land = False
        if isinstance(animal, (Penguin, Seal)):
            config = get_config()
            energy_percent = animal.energy / animal.max_energy
            if animal.breeding_cooldown == 0 and energy_percent >= config.ENERGY_THRESHOLD_BREEDING:
                needs_land = True # Go to land to breed
            elif energy_percent > config.ENERGY_THRESHOLD_HIGH:
                needs_land = True # Go to land for socializing when energy > 90%
        elif isinstance(animal, Seagull):
            config = get_config()
            energy_percent = animal.energy / animal.max_energy
            # Carrying fish has highest landing priority: return to floe before eating.
            if animal.carrying_fish:
                needs_land = True
                if animal.state == "flying":
                    animal.behavior_state = "carrying_to_land"
            # Seagull: when energy > 90%, go to ice floe to socialize/breed
            elif energy_percent > config.ENERGY_THRESHOLD_HIGH:
                needs_land = True
            # When flying + idle: must go to land (idle only when grounded)
            elif animal.state == "flying" and animal.behavior_state == "idle":
                needs_land = True
            # When energy < 60%, take off to hunt (stay flying)
            elif energy_percent < config.ENERGY_THRESHOLD_HUNTING and animal.state == "grounded":
                animal.state = "flying"  # Take off to hunt
        
        if needs_land and (not is_on_land if not isinstance(animal, Seagull) else (animal.state == "flying" or not is_on_land)):
            # Seagull: fly toward grounded seagulls only; land when arriving on their floe
            if isinstance(animal, Seagull):
                grounded_seagulls = [g for g in self.world.seagulls if g.id != animal.id and g.is_alive() and g.state == "grounded"]
                if grounded_seagulls:
                    nearest_grounded = min(grounded_seagulls, key=lambda g: (g.x - animal.x)**2 + (g.y - animal.y)**2)
                    dx = nearest_grounded.x - animal.x
                    dy = nearest_grounded.y - animal.y
                else:
                    floes = self.world.environment.ice_floes
                    if floes:
                        nearest_floe = min(floes, key=lambda f: (f['x']-animal.x)**2 + (f['y']-animal.y)**2)
                        dx = nearest_floe['x'] - animal.x
                        dy = nearest_floe['y'] - animal.y
                    else:
                        dx, dy = 0, 0
                if is_on_land:
                    animal.state = "grounded"
                    if animal.carrying_fish and animal.prey_processing_ticks <= 0:
                        animal.behavior_state = "processing_prey"
                        animal.prey_processing_ticks = config.SEAGULL_PREY_PROCESSING_TICKS
            else:
                # Penguin/Seal: go to nearest ice floe
                floes = self.world.environment.ice_floes
                if floes:
                    nearest_floe = min(floes, key=lambda f: (f['x']-animal.x)**2 + (f['y']-animal.y)**2)
                    dx = nearest_floe['x'] - animal.x
                    dy = nearest_floe['y'] - animal.y
        
        # 1a. Seagull flee - trigger on floe, continue countdown while flying.
        if isinstance(animal, Seagull):
            config = get_config()
            if animal.state == "grounded":
                threats = [t for t in (list(self.world.seals) + list(self.world.penguins)) if t.is_alive()]
                if animal.carrying_fish and animal.behavior_state != "processing_prey":
                    animal.behavior_state = "processing_prey"
                    if animal.prey_processing_ticks <= 0:
                        animal.prey_processing_ticks = config.SEAGULL_PREY_PROCESSING_TICKS
                # Use linear search for accurate distances (spatial grid may have stale positions)
                nearest_threat = None
                min_dist = config.SEAGULL_FLEE_RANGE_GROUNDED
                for t in threats:
                    d = animal.distance_to(t)
                    if d < min_dist:
                        min_dist = d
                        nearest_threat = t
                if nearest_threat and animal.behavior_state != "fleeing":
                    # While processing prey on floe, any close threat forces prey drop.
                    if animal.carrying_fish:
                        self._drop_seagull_fish(animal)
                    animal.state = "flying"
                    animal.behavior_state = "fleeing"
                    animal.flee_cooldown = config.FLEE_COOLDOWN_TICKS
                    base_dx = animal.x - nearest_threat.x
                    base_dy = animal.y - nearest_threat.y
                    base_flee_angle = math.atan2(base_dy, base_dx) if (base_dx != 0 or base_dy != 0) else random.uniform(0, 2 * math.pi)
                    angle_variation = random.uniform(-config.FLEE_ANGLE_VARIATION, config.FLEE_ANGLE_VARIATION)
                    flee_angle = (base_flee_angle + angle_variation) % (2 * math.pi)
                    temp_dx = math.cos(flee_angle) * 100
                    temp_dy = math.sin(flee_angle) * 100
                    constrained_dx, constrained_dy = self._constrain_direction_near_edge(animal, temp_dx, temp_dy)
                    animal.flee_edge_direction = math.atan2(constrained_dy, constrained_dx)
                    target = nearest_threat

            if animal.behavior_state == "fleeing" and animal.flee_cooldown > 0:
                animal.state = "flying"
                animal.flee_cooldown -= 1
                flee_distance = config.FLEE_DISTANCE_MIN + random.uniform(0, config.FLEE_DISTANCE_MAX - config.FLEE_DISTANCE_MIN)
                dx = math.cos(animal.flee_edge_direction) * flee_distance
                dy = math.sin(animal.flee_edge_direction) * flee_distance
                dx, dy = self._constrain_direction_near_edge(animal, dx, dy)
            elif animal.behavior_state == "fleeing" and animal.flee_cooldown == 0:
                energy_percent = animal.energy / animal.max_energy
                if energy_percent < config.ENERGY_THRESHOLD_HUNTING:
                    animal.behavior_state = "searching"
                    animal.hunt_direction_angle = random.uniform(0, 2 * math.pi)
                    animal.hunt_direction_ticks = random.randint(config.SEAGULL_HUNTING_DIRECTION_TICKS_MIN, config.SEAGULL_HUNTING_DIRECTION_TICKS_MAX)
                else:
                    animal.behavior_state = "idle"
                animal.hunt_direction_ticks = 0

            # Grounded with fish and no immediate flee: keep processing countdown.
            if animal.carrying_fish and animal.behavior_state == "processing_prey" and animal.state == "grounded":
                seagull_processing_locked = True
                dx, dy = 0, 0
                if animal.prey_processing_ticks > 0:
                    animal.prey_processing_ticks -= 1
                if animal.prey_processing_ticks <= 0:
                    animal.carrying_fish = False
                    animal.prey_processing_ticks = 0
                    animal.gain_energy(config.SEAGULL_ENERGY_RECOVERY_FISH)
                    animal.hunting_cooldown = config.HUNTING_COOLDOWN_TICKS
                    animal.behavior_state = "idle"

        # 1.5. Update behavior state based on energy (BEFORE social so searching overrides grouping)
        if isinstance(animal, (Penguin, Seal, Seagull)):
            energy_percent = animal.energy / animal.max_energy
            config = get_config()
            is_seagull_locked_prey_flow = (
                isinstance(animal, Seagull) and
                (animal.carrying_fish or animal.behavior_state in ["carrying_to_land", "processing_prey"])
            )
            if is_seagull_locked_prey_flow:
                pass
            elif energy_percent < config.ENERGY_THRESHOLD_HUNTING and energy_percent <= config.ENERGY_THRESHOLD_HIGH and animal.behavior_state not in ["fleeing", "targeting"] and animal.hunting_cooldown == 0:
                if animal.behavior_state != "searching":
                    animal.behavior_state = "searching"
                    animal.hunt_direction_angle = random.uniform(0, 2 * math.pi)
                    animal.hunt_direction_ticks = random.randint(15, 40)
            elif energy_percent >= config.ENERGY_THRESHOLD_HUNTING and animal.behavior_state == "searching":
                animal.behavior_state = "idle"
                animal.hunt_direction_ticks = 0
            elif energy_percent > config.ENERGY_THRESHOLD_HIGH and animal.behavior_state in ["searching", "targeting"]:
                animal.behavior_state = "idle"
                animal.target_id = ""
                animal.hunt_direction_ticks = 0

        # 1b. Social behavior - skip when searching (searching has higher priority)
        # Seagull: when grounded and energy > 90%, socialize with other grounded seagulls
        if isinstance(animal, Seagull) and not seagull_processing_locked and dx == 0 and dy == 0 and animal.state == "grounded" and \
           animal.behavior_state not in ["fleeing", "targeting", "searching", "processing_prey"] and \
           not animal.carrying_fish:
            config = get_config()
            energy_percent = animal.energy / animal.max_energy
            if energy_percent > config.ENERGY_THRESHOLD_HIGH:
                same_type = [g for g in self.world.seagulls if g.id != animal.id and g.is_alive() and g.state == "grounded" and g.behavior_state == "idle"]
                nearby = [a for a in same_type if animal.distance_to(a) < 50]
                if nearby:
                    if len(nearby) > 3:
                        center_x = sum(a.x for a in nearby) / len(nearby)
                        center_y = sum(a.y for a in nearby) / len(nearby)
                        dx = animal.x - center_x
                        dy = animal.y - center_y
                        if abs(dx) < 5 and abs(dy) < 5:
                            dx += random.uniform(-20, 20)
                            dy += random.uniform(-20, 20)
                    else:
                        target_animal = random.choice(nearby)
                        dx = target_animal.x - animal.x
                        dy = target_animal.y - animal.y
                        if abs(dx) < 3 and abs(dy) < 3:
                            angle = random.uniform(0, 2 * math.pi)
                            dx += math.cos(angle) * 10
                            dy += math.sin(angle) * 10

        # Penguin/Seal social behavior (dispersal) - skip when searching (searching has higher priority)
        if isinstance(animal, (Penguin, Seal)) and dx == 0 and dy == 0 and \
           animal.behavior_state not in ["fleeing", "targeting", "searching"]:
            energy_percent = animal.energy / animal.max_energy
            config = get_config()
            has_energy_for_social = energy_percent > config.ENERGY_THRESHOLD_SOCIAL  # Only socialize when energy > threshold
            
            if is_on_land:
                # On land: Social behavior depends on energy level
                same_type = [p for p in self.world.penguins if isinstance(animal, Penguin) and p.id != animal.id and p.is_alive() and p.state == "land"]
                if isinstance(animal, Seal):
                    same_type = [s for s in self.world.seals if s.id != animal.id and s.is_alive() and s.state == "land"]
                
                if same_type:
                    nearby = [a for a in same_type if animal.distance_to(a) < 150]  # Social grouping range 3x (was 50)
                    # Huddling only considers idle same-species; dispersal considers all
                    nearby_idle = [a for a in nearby if a.behavior_state == "idle"]
                    if nearby:
                        if has_energy_for_social and nearby_idle:
                            # Energy > 60%: Social grouping behavior (huddling) - only with idle
                            # If too crowded (more than 3 nearby idle), move away slightly
                            if len(nearby_idle) > 3:
                                # Move away from center of nearby idle animals
                                center_x = sum(a.x for a in nearby_idle) / len(nearby_idle)
                                center_y = sum(a.y for a in nearby_idle) / len(nearby_idle)
                                dx = animal.x - center_x
                                dy = animal.y - center_y
                                # Ensure meaningful movement
                                if abs(dx) < 5 and abs(dy) < 5:
                                    # Too small, add random component
                                    dx += random.uniform(-20, 20)
                                    dy += random.uniform(-20, 20)
                            else:
                                # Move towards a nearby idle animal (social grouping - huddling)
                                target_animal = random.choice(nearby_idle)
                                dx = target_animal.x - animal.x
                                dy = target_animal.y - animal.y
                                # Make movement subtle for gentle grouping
                                if abs(dx) < 3 and abs(dy) < 3:
                                    # Very close, add small exploration component
                                    angle = random.uniform(0, 2 * math.pi)
                                    dx += math.cos(angle) * 10
                                    dy += math.sin(angle) * 10
                        else:
                            # Energy <= 60%: Dispersal behavior (no huddling)
                            # Move away from nearby animals to conserve energy and avoid competition
                            center_x = sum(a.x for a in nearby) / len(nearby)
                            center_y = sum(a.y for a in nearby) / len(nearby)
                            dx = animal.x - center_x
                            dy = animal.y - center_y
                            
                            # Ensure meaningful dispersal movement
                            if abs(dx) < 5 and abs(dy) < 5:
                                # Too close to center, pick random direction away
                                angle = random.uniform(0, 2 * math.pi)
                                dx = math.cos(angle) * 40
                                dy = math.sin(angle) * 40
                            else:
                                # Amplify the away direction for better dispersal
                                dx *= 1.5
                                dy *= 1.5
            else:
                # In sea: Always active dispersal behavior (spread out for foraging)
                # Avoid clustering with same type animals to spread out for foraging
                same_type = [p for p in self.world.penguins if isinstance(animal, Penguin) and p.id != animal.id and p.is_alive() and p.state == "sea"]
                if isinstance(animal, Seal):
                    same_type = [s for s in self.world.seals if s.id != animal.id and s.is_alive() and s.state == "sea"]
                
                if same_type:
                    # Find nearby animals of same type
                    nearby = [a for a in same_type if animal.distance_to(a) < 80]
                    if nearby:
                        # Move away from nearby animals to disperse
                        center_x = sum(a.x for a in nearby) / len(nearby)
                        center_y = sum(a.y for a in nearby) / len(nearby)
                        # Calculate direction away from the group
                        dx = animal.x - center_x
                        dy = animal.y - center_y
                        
                        # If too close to center (very clustered), move more aggressively
                        dist_to_center = math.sqrt(dx*dx + dy*dy)
                        if dist_to_center < 30:
                            # Very clustered, move away more strongly
                            if abs(dx) < 0.1 and abs(dy) < 0.1:
                                # At center, pick random direction
                                angle = random.uniform(0, 2 * math.pi)
                                dx = math.cos(angle) * 50
                                dy = math.sin(angle) * 50
                            else:
                                # Amplify the away direction
                                dx *= 2.0
                                dy *= 2.0
                        else:
                            # Moderate distance, gentle dispersal
                            if abs(dx) < 5 and abs(dy) < 5:
                                # Add random component for natural dispersal
                                angle = random.uniform(0, 2 * math.pi)
                                dx += math.cos(angle) * 30
                                dy += math.sin(angle) * 30
        
        # 2. Safety (Avoid Predators) - Penguins should flee from Seals
        if isinstance(animal, Penguin):
            predators = [s for s in self.world.seals if s.is_alive()]
            # Perception range depends on location: smaller on land, larger in sea
            # On land, penguins have reduced awareness (harder to detect seals)
            # In sea, penguins have better awareness (easier to detect seals)
            config = get_config()
            if is_on_land:
                perception_range = config.PENGUIN_PERCEPTION_LAND
            else:
                perception_range = config.PENGUIN_PERCEPTION_SEA
            nearest_predator = self._find_nearest(animal, predators, max_distance=perception_range)
            
            if nearest_predator and animal.behavior_state != "fleeing":
                # Flee! Change to fleeing state (highest priority: flee > target > disperse > hunt)
                animal.behavior_state = "fleeing"
                # Set flee cooldown (3 seconds at 5 ticks/sec)
                config = get_config()
                animal.flee_cooldown = config.FLEE_COOLDOWN_TICKS
                
                # Calculate base fleeing direction (away from predator)
                base_dx = animal.x - nearest_predator.x
                base_dy = animal.y - nearest_predator.y
                base_flee_angle = math.atan2(base_dy, base_dx) if (base_dx != 0 or base_dy != 0) else random.uniform(0, 2 * math.pi)
                
                # Add random variation to fleeing direction (±45 degrees)
                config = get_config()
                angle_variation = random.uniform(-config.FLEE_ANGLE_VARIATION, config.FLEE_ANGLE_VARIATION)
                flee_angle = (base_flee_angle + angle_variation) % (2 * math.pi)
                
                # Constrain direction to avoid hitting boundaries
                temp_dx = math.cos(flee_angle) * 100  # Use a large vector for direction calculation
                temp_dy = math.sin(flee_angle) * 100
                constrained_dx, constrained_dy = self._constrain_direction_near_edge(animal, temp_dx, temp_dy)
                flee_angle = math.atan2(constrained_dy, constrained_dx)
                
                # Store the fleeing direction (fixed for 3 seconds, won't change)
                animal.flee_edge_direction = flee_angle
                
                target = nearest_predator # Just to mark as "busy" so we don't hunt while fleeing
            
            # If already in fleeing state, continue fleeing in fixed direction for 3 seconds
            if animal.behavior_state == "fleeing":
                if animal.flee_cooldown > 0:
                    # Still fleeing: continue in fixed direction, don't change direction or stop
                    animal.flee_cooldown -= 1
                    # Move in the fixed fleeing direction
                    # Direction was already constrained when fleeing started, so use it directly
                    config = get_config()
                    flee_distance = config.FLEE_DISTANCE_MIN + random.uniform(0, config.FLEE_DISTANCE_MAX - config.FLEE_DISTANCE_MIN)
                    dx = math.cos(animal.flee_edge_direction) * flee_distance
                    dy = math.sin(animal.flee_edge_direction) * flee_distance
                    # Re-apply boundary constraint to ensure we don't hit boundaries
                    # This adjusts the movement vector but keeps the stored direction fixed
                    dx, dy = self._constrain_direction_near_edge(animal, dx, dy)
                    # Note: We don't update flee_edge_direction here to keep it fixed for 3 seconds
                else:
                    # 3 seconds passed, exit fleeing state
                    config = get_config()
                    energy_percent = animal.energy / animal.max_energy
                    if energy_percent < config.ENERGY_THRESHOLD_HUNTING:
                        animal.behavior_state = "searching"
                        # Initialize new searching direction
                        animal.hunt_direction_angle = random.uniform(0, 2 * math.pi)
                        animal.hunt_direction_ticks = random.randint(config.HUNTING_DIRECTION_TICKS_MIN, config.HUNTING_DIRECTION_TICKS_MAX)
                    else:
                        animal.behavior_state = "idle"
                    animal.hunt_direction_ticks = 0
        
        # 2.5. Seagull searching - same pattern as penguin/seal (fly one direction 2-3 sec, then turn), just faster
        if not seagull_processing_locked and not target and isinstance(animal, Seagull) and not animal.carrying_fish and animal.behavior_state == "searching" and animal.hunting_cooldown == 0:
            energy_percent = animal.energy / animal.max_energy
            config = get_config()
            if energy_percent <= config.ENERGY_THRESHOLD_HIGH:
                # Low energy: take off if grounded to hunt
                if animal.state == "grounded":
                    animal.state = "flying"
                # Same pattern as penguin/seal: fly in one direction for 2-3 seconds, then random turn
                if animal.hunt_direction_ticks <= 0:
                    animal.hunt_direction_ticks = random.randint(config.SEAGULL_HUNTING_DIRECTION_TICKS_MIN, config.SEAGULL_HUNTING_DIRECTION_TICKS_MAX)
                    animal.hunt_direction_angle = random.uniform(0, 2 * math.pi)
                animal.hunt_direction_ticks -= 1
                search_distance = 30 + random.uniform(0, 20)  # Same step size as penguin/seal (speed comes from animal speed)
                dx = math.cos(animal.hunt_direction_angle) * search_distance
                dy = math.sin(animal.hunt_direction_angle) * search_distance
                # Check for fish (seagull has larger search range)
                valid_fish = [f for f in self.world.fish if f.is_alive()]
                nearby_fish = self._find_nearest(animal, valid_fish, max_distance=config.SEAGULL_PREY_SEARCH_RANGE)
                if nearby_fish:
                    animal.behavior_state = "targeting"
                    animal.target_id = nearby_fish.id
                    target = nearby_fish
                    dx = nearby_fish.x - animal.x
                    dy = nearby_fish.y - animal.y
                    animal.hunt_direction_ticks = 0

        # 2.6. Seagull targeting fish
        if not seagull_processing_locked and not target and isinstance(animal, Seagull) and not animal.carrying_fish and animal.behavior_state == "targeting":
            target_fish = None
            for f in self.world.fish:
                if f.is_alive() and f.id == animal.target_id:
                    target_fish = f
                    break
            config = get_config()
            if target_fish and animal.distance_to(target_fish) <= config.MAX_TRACKING_DISTANCE:
                dx = target_fish.x - animal.x
                dy = target_fish.y - animal.y
                target = target_fish
            else:
                animal.target_id = ""
                energy_percent = animal.energy / animal.max_energy
                if energy_percent < config.ENERGY_THRESHOLD_HUNTING:
                    animal.behavior_state = "searching"
                    animal.hunt_direction_angle = random.uniform(0, 2 * math.pi)
                    animal.hunt_direction_ticks = random.randint(config.SEAGULL_HUNTING_DIRECTION_TICKS_MIN, config.SEAGULL_HUNTING_DIRECTION_TICKS_MAX)
                else:
                    animal.behavior_state = "idle"

        # 3. Searching Behavior - Penguin, Seal
        if not target and isinstance(animal, (Penguin, Seal)) and animal.behavior_state == "searching" and animal.hunting_cooldown == 0:
            energy_percent = animal.energy / animal.max_energy
            # Don't search if energy > high threshold (should be socializing on land instead)
            config = get_config()
            if energy_percent <= config.ENERGY_THRESHOLD_HIGH:
                # On floes, searching penguins/seals will opportunistically approach dropped fish.
                # Land scavenging unified behavior:
                # - approach nearest dropped floe fish
                # - or approach a grounded seagull currently processing prey
                # (likely to trigger a flee+drop event nearby).
                land_food_target = self._find_nearest_land_food_source(animal, max_distance=config.PREY_SEARCH_RANGE) if is_on_land else None
                if land_food_target is not None:
                    target = land_food_target
                    dx = land_food_target.x - animal.x
                    dy = land_food_target.y - animal.y
                # On land with energy < 60%: go straight toward sea (until in water)
                elif is_on_land and energy_percent < config.ENERGY_THRESHOLD_HUNTING:
                    # Seal: first check for very close penguin to hunt
                    nearby_penguin = None
                    if isinstance(animal, Seal):
                        land_penguins = [p for p in self.world.penguins if p.is_alive() and p.id != animal.id and p.state == "land"]
                        nearby_penguin = self._find_nearest(animal, land_penguins, max_distance=config.SEAL_LAND_PENGUIN_HUNT_RANGE)
                    
                    if nearby_penguin:
                        # Seal found close penguin - hunt it
                        animal.behavior_state = "targeting"
                        animal.target_id = nearby_penguin.id
                        target = nearby_penguin
                        dx = nearby_penguin.x - animal.x
                        dy = nearby_penguin.y - animal.y
                        animal.hunt_direction_ticks = 0
                    else:
                        # Penguin or Seal with no close penguin: move toward nearest sea direction.
                        # Re-evaluate regularly so animals can escape overlapping/irregular floes.
                        if animal.hunt_direction_ticks <= 0:
                            sea_direction = self._find_direction_to_nearest_sea(animal.x, animal.y)
                            if sea_direction is not None:
                                animal.hunt_direction_angle = sea_direction
                            else:
                                # Fallback to center-away direction if sea search fails.
                                nearest_floe = None
                                min_dist = float('inf')
                                for floe in self.world.environment.ice_floes:
                                    dist = math.sqrt((animal.x - floe['x'])**2 + (animal.y - floe['y'])**2)
                                    if dist < min_dist:
                                        min_dist = dist
                                        nearest_floe = floe

                                if nearest_floe:
                                    away_dx = animal.x - nearest_floe['x']
                                    away_dy = animal.y - nearest_floe['y']
                                    dist = math.sqrt(away_dx * away_dx + away_dy * away_dy)
                                    if dist > 0:
                                        animal.hunt_direction_angle = math.atan2(away_dy, away_dx)
                                    else:
                                        animal.hunt_direction_angle = random.uniform(0, 2 * math.pi)
                                else:
                                    animal.hunt_direction_angle = random.uniform(0, 2 * math.pi)

                            animal.hunt_direction_ticks = 5

                        animal.hunt_direction_ticks -= 1
                        dx = math.cos(animal.hunt_direction_angle) * 50
                        dy = math.sin(animal.hunt_direction_angle) * 50
                else:
                    # In sea: normal searching (random direction, but prefer away from floe if too close)
                    if animal.hunt_direction_ticks <= 0:
                        config = get_config()
                        animal.hunt_direction_ticks = random.randint(config.HUNTING_DIRECTION_TICKS_MIN, config.HUNTING_DIRECTION_TICKS_MAX)
                        # Check if too close to any floe - if so, prefer swimming away
                        nearest_floe = None
                        min_dist = float('inf')
                        for floe in self.world.environment.ice_floes:
                            dist = math.sqrt((animal.x - floe['x'])**2 + (animal.y - floe['y'])**2)
                            if dist < min_dist:
                                min_dist = dist
                                nearest_floe = floe
                        if nearest_floe and min_dist < config.SEA_SEARCH_AVOID_FLOE_RANGE:
                            # Prefer direction away from floe, with some random variation
                            away_dx = animal.x - nearest_floe['x']
                            away_dy = animal.y - nearest_floe['y']
                            away_angle = math.atan2(away_dy, away_dx)
                            # Add random variation (±45 degrees)
                            animal.hunt_direction_angle = away_angle + random.uniform(-0.785398, 0.785398)
                            animal.hunt_direction_angle = animal.hunt_direction_angle % (2 * math.pi)
                        else:
                            animal.hunt_direction_angle = random.uniform(0, 2 * math.pi)
                    
                    animal.hunt_direction_ticks -= 1
                    search_distance = 30 + random.uniform(0, 20)
                    dx = math.cos(animal.hunt_direction_angle) * search_distance
                    dy = math.sin(animal.hunt_direction_angle) * search_distance
                
                # Check for prey while searching (only when in sea, or seal targeting penguin already handled above)
                if target is None and not (is_on_land and energy_percent < config.ENERGY_THRESHOLD_HUNTING):
                    prey_type = None
                    if isinstance(animal, Penguin) and animal.state == "sea":
                        prey_type = Fish
                    elif isinstance(animal, Seal):
                        prey_type = (Penguin, Fish) if animal.state == "sea" else Penguin
                
                    if prey_type:
                        potential_prey = []
                        if isinstance(prey_type, tuple):
                            for t in prey_type:
                                if t == Penguin: potential_prey.extend(self.world.penguins)
                                if t == Fish: potential_prey.extend(self.world.fish)
                        elif prey_type == Penguin:
                            potential_prey = self.world.penguins
                        elif prey_type == Fish:
                            potential_prey = self.world.fish
                        
                        # For seals, prioritize sea targets
                        if isinstance(animal, Seal):
                            sea_prey = [p for p in potential_prey 
                                       if p.is_alive() and p != animal and 
                                       (isinstance(p, Fish) or p.state == "sea")]
                            land_prey = [p for p in potential_prey 
                                        if p.is_alive() and p != animal and 
                                        isinstance(p, Penguin) and p.state == "land"]
                            
                            # Prioritize sea targets if both are available
                            config = get_config()
                            sea_target = self._find_nearest(animal, sea_prey, max_distance=config.PREY_SEARCH_RANGE)
                            land_target = self._find_nearest(animal, land_prey, max_distance=config.PREY_SEARCH_RANGE)
                            
                            # Prefer sea target if both are available
                            if sea_target and land_target:
                                nearby_prey = sea_target
                            elif sea_target:
                                nearby_prey = sea_target
                            elif land_target:
                                nearby_prey = land_target
                            else:
                                nearby_prey = None
                        else:
                            valid_prey = [
                                p for p in potential_prey 
                                if p.is_alive() and p != animal and 
                                (isinstance(p, Fish) or p.state == animal.state)
                            ]
                            
                            # Look for nearby prey
                            config = get_config()
                            nearby_prey = self._find_nearest(animal, valid_prey, max_distance=config.PREY_SEARCH_RANGE)
                        
                        if nearby_prey:
                            # Found prey! Switch from searching to targeting
                            animal.behavior_state = "targeting"
                            animal.target_id = nearby_prey.id  # Store target ID for tracking
                            target = nearby_prey
                            dx = nearby_prey.x - animal.x
                            dy = nearby_prey.y - animal.y
                            # Reset direction timer
                            animal.hunt_direction_ticks = 0
        
        # 3a. Targeting prey - when found prey during searching
        if not target and isinstance(animal, (Penguin, Seal)) and animal.behavior_state == "targeting":
            prey_type = None
            if isinstance(animal, Penguin) and animal.state == "sea":
                prey_type = Fish
            elif isinstance(animal, Seal):
                prey_type = (Penguin, Fish) if animal.state == "sea" else Penguin
            
            if prey_type:
                potential_prey = []
                if isinstance(prey_type, tuple):
                    for t in prey_type:
                        if t == Penguin: potential_prey.extend(self.world.penguins)
                        if t == Fish: potential_prey.extend(self.world.fish)
                elif prey_type == Penguin:
                    potential_prey = self.world.penguins
                elif prey_type == Fish:
                    potential_prey = self.world.fish
                
                # For seals, prioritize sea targets
                if isinstance(animal, Seal):
                    sea_prey = [p for p in potential_prey 
                               if p.is_alive() and p != animal and 
                               (isinstance(p, Fish) or p.state == "sea")]
                    land_prey = [p for p in potential_prey 
                                if p.is_alive() and p != animal and 
                                isinstance(p, Penguin) and p.state == "land"]
                    
                    # First check tracked target
                    tracked_sea = None
                    tracked_land = None
                    if animal.target_id:
                        for p in sea_prey:
                            if p.id == animal.target_id:
                                tracked_sea = p
                                break
                        if not tracked_sea:
                            for p in land_prey:
                                if p.id == animal.target_id:
                                    tracked_land = p
                                    break
                    
                    # Prioritize tracked sea target, then any sea target, then tracked land target, then any land target
                    config = get_config()
                    if tracked_sea and animal.distance_to(tracked_sea) <= config.MAX_TRACKING_DISTANCE:
                        target = tracked_sea
                        dx = tracked_sea.x - animal.x
                        dy = tracked_sea.y - animal.y
                    else:
                        # Look for any sea target first
                        sea_target = self._find_nearest(animal, sea_prey, max_distance=config.MAX_TRACKING_DISTANCE)
                        if sea_target:
                            target = sea_target
                            animal.target_id = sea_target.id
                            dx = sea_target.x - animal.x
                            dy = sea_target.y - animal.y
                        elif tracked_land and animal.distance_to(tracked_land) <= config.MAX_TRACKING_DISTANCE:
                            target = tracked_land
                            dx = tracked_land.x - animal.x
                            dy = tracked_land.y - animal.y
                        else:
                            # Look for any land target
                            land_target = self._find_nearest(animal, land_prey, max_distance=config.MAX_TRACKING_DISTANCE)
                            if land_target:
                                target = land_target
                                animal.target_id = land_target.id
                                dx = land_target.x - animal.x
                                dy = land_target.y - animal.y
                            else:
                                # No target found, give up
                                animal.target_id = ""
                                energy_percent = animal.energy / animal.max_energy
                                if energy_percent < config.ENERGY_THRESHOLD_HUNTING:
                                    animal.behavior_state = "searching"
                                    animal.hunt_direction_angle = random.uniform(0, 2 * math.pi)
                                    animal.hunt_direction_ticks = random.randint(config.HUNTING_DIRECTION_TICKS_MIN, config.HUNTING_DIRECTION_TICKS_MAX)
                                else:
                                    animal.behavior_state = "idle"
                                    animal.hunt_direction_ticks = 0
                else:
                    # For penguins, use original logic
                    valid_prey = [
                        p for p in potential_prey 
                        if p.is_alive() and p != animal and 
                        (isinstance(p, Fish) or p.state == animal.state)
                    ]
                    
                    # First, try to find the specific target we were tracking (if we have a target_id)
                    tracked_prey = None
                    if animal.target_id:
                        for p in valid_prey:
                            if p.id == animal.target_id:
                                tracked_prey = p
                                break
                    
                    # If we found the tracked prey, check distance
                    if tracked_prey:
                        distance_to_target = animal.distance_to(tracked_prey)
                        config = get_config()
                        max_tracking_distance = config.MAX_TRACKING_DISTANCE  # Maximum distance before giving up
                        
                        if distance_to_target <= max_tracking_distance:
                            # Target is still within range, continue tracking
                            target = tracked_prey
                            dx = tracked_prey.x - animal.x
                            dy = tracked_prey.y - animal.y
                        else:
                            # Target is too far away, give up tracking
                            config = get_config()
                            animal.target_id = ""  # Clear target ID
                            energy_percent = animal.energy / animal.max_energy
                            if energy_percent < config.ENERGY_THRESHOLD_HUNTING:
                                animal.behavior_state = "searching"  # Return to searching
                                animal.hunt_direction_angle = random.uniform(0, 2 * math.pi)
                                animal.hunt_direction_ticks = random.randint(config.HUNTING_DIRECTION_TICKS_MIN, config.HUNTING_DIRECTION_TICKS_MAX)
                            else:
                                animal.behavior_state = "idle"
                                animal.hunt_direction_ticks = 0
                    else:
                        # Lost the specific target, look for any nearby prey
                        # Look for nearby prey (within 300 units when targeting)
                        nearby_prey = self._find_nearest(animal, valid_prey, max_distance=300)
                        if nearby_prey:
                            # Found a new nearby prey, switch to it
                            target = nearby_prey
                            animal.target_id = nearby_prey.id  # Store the new target ID
                            dx = nearby_prey.x - animal.x
                            dy = nearby_prey.y - animal.y
                        else:
                            # No prey found, give up tracking
                            config = get_config()
                            animal.target_id = ""  # Clear target ID
                            energy_percent = animal.energy / animal.max_energy
                            if energy_percent < config.ENERGY_THRESHOLD_HUNTING:
                                animal.behavior_state = "searching"  # Return to searching
                                animal.hunt_direction_angle = random.uniform(0, 2 * math.pi)
                                animal.hunt_direction_ticks = random.randint(config.HUNTING_DIRECTION_TICKS_MIN, config.HUNTING_DIRECTION_TICKS_MAX)
                            else:
                                animal.behavior_state = "idle"
                                animal.hunt_direction_ticks = 0
        
        # 3b. Regular Hunting (when not in searching/targeting mode, but still looking for food)
        # Penguins and Seals actively hunt even when not very hungry to explore and find food
        # But not if in hunting cooldown (recently ate) or energy > 90% (socializing)
        if not target and isinstance(animal, (Penguin, Seal)) and animal.behavior_state not in ["searching", "targeting"] and animal.hunting_cooldown == 0:
            energy_percent = animal.energy / animal.max_energy
            # Don't hunt if energy > high threshold (should be socializing on land instead)
            config = get_config()
            if energy_percent <= config.ENERGY_THRESHOLD_HIGH:
                prey_type = None
                hunting_threshold = 1.0  # Always hunt (no energy threshold)
                
                if isinstance(animal, Penguin) and animal.state == "sea":
                    prey_type = Fish
                elif isinstance(animal, Seal):
                    # Seals hunt Penguins everywhere (prioritized) or Fish in sea
                    prey_type = (Penguin, Fish) if animal.state == "sea" else Penguin
                
                if prey_type and animal.energy < animal.max_energy * hunting_threshold:
                    # Find prey with increased search range for better exploration
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
                    
                    # Increased search range for better exploration
                    config = get_config()
                    target = self._find_nearest(animal, valid_prey, max_distance=config.PREY_EXPLORATION_RANGE)
                    if target:
                        dx = target.x - animal.x
                        dy = target.y - animal.y
        
        # 4. Active Exploration (if no other drive, for Penguins, Seals, Seagulls)
        if dx == 0 and dy == 0:
            if isinstance(animal, (Penguin, Seal, Seagull)):
                if not (
                    isinstance(animal, Seagull) and (
                        (animal.carrying_fish and animal.state == "grounded") or seagull_processing_locked
                    )
                ):
                    # Seagull flying: explore entire map. Grounded: explore floe.
                    explore_on_land = is_on_land if not isinstance(animal, Seagull) else (animal.state == "grounded" and is_on_land)
                    # On land (or grounded on floe), explore the ice floe; in sea (or flying), explore
                    if explore_on_land:
                        # Explore within the current ice floe or move to edge to go to sea
                        # Find current floe
                        current_floe = None
                        for floe in self.world.environment.ice_floes:
                            dist_sq = (animal.x - floe['x'])**2 + (animal.y - floe['y'])**2
                            if dist_sq <= floe['radius']**2:
                                current_floe = floe
                                break
                        
                        if current_floe:
                            # Explore within the ice floe - move around actively
                            # Choose a random point within the floe to explore
                            angle = random.uniform(0, 2 * math.pi)
                            # Move a good distance within the floe (30-60% of radius)
                            exploration_distance = current_floe['radius'] * random.uniform(0.3, 0.6)
                            target_x = current_floe['x'] + math.cos(angle) * exploration_distance
                            target_y = current_floe['y'] + math.sin(angle) * exploration_distance
                            
                            # Move towards that point
                            dx = target_x - animal.x
                            dy = target_y - animal.y
                            
                            # Ensure minimum movement distance
                            if abs(dx) < 10 and abs(dy) < 10:
                                # Too small, add more exploration
                                angle2 = random.uniform(0, 2 * math.pi)
                                additional_dist = 20 + random.uniform(0, 30)
                                dx += math.cos(angle2) * additional_dist
                                dy += math.sin(angle2) * additional_dist
                        else:
                            # Not on a floe (shouldn't happen), but handle it with active exploration
                            angle = random.uniform(0, 2 * math.pi)
                            exploration_distance = 30 + random.uniform(0, 50)
                            dx = math.cos(angle) * exploration_distance
                            dy = math.sin(angle) * exploration_distance
                    else:
                        # In sea (or flying for seagull): explore - same direction persistence as searching
                        # Walk one direction for a few seconds, then randomly change
                        config = get_config()
                        if animal.hunt_direction_ticks <= 0:
                            animal.hunt_direction_ticks = random.randint(config.HUNTING_DIRECTION_TICKS_MIN, config.HUNTING_DIRECTION_TICKS_MAX)
                            # If too close to floe, prefer swimming away (same as searching)
                            if isinstance(animal, (Penguin, Seal)):
                                nearest_floe = None
                                min_dist = float('inf')
                                for floe in self.world.environment.ice_floes:
                                    dist = math.sqrt((animal.x - floe['x'])**2 + (animal.y - floe['y'])**2)
                                    if dist < min_dist:
                                        min_dist = dist
                                        nearest_floe = floe
                                if nearest_floe and min_dist < config.SEA_SEARCH_AVOID_FLOE_RANGE:
                                    away_dx = animal.x - nearest_floe['x']
                                    away_dy = animal.y - nearest_floe['y']
                                    away_angle = math.atan2(away_dy, away_dx)
                                    animal.hunt_direction_angle = away_angle + random.uniform(-0.785398, 0.785398)
                                    animal.hunt_direction_angle = animal.hunt_direction_angle % (2 * math.pi)
                                else:
                                    animal.hunt_direction_angle = random.uniform(0, 2 * math.pi)
                            else:
                                animal.hunt_direction_angle = random.uniform(0, 2 * math.pi)
                        animal.hunt_direction_ticks -= 1
                        exploration_distance = 50 + random.uniform(0, 100)  # 50-150 units
                        dx = math.cos(animal.hunt_direction_angle) * exploration_distance
                        dy = math.sin(animal.hunt_direction_angle) * exploration_distance
            else:
                # Fish: smaller random movement
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
        
        # Constrain movement direction near edges (before normalization)
        # If animal is near an edge, limit movement direction to 180 degrees facing inward
        if dx != 0 or dy != 0:
            dx, dy = self._constrain_direction_near_edge(animal, dx, dy)
        
        # Normalize and apply speed
        # For exploration movements, don't over-normalize to preserve exploration distance
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            # Ensure speed is not zero to avoid division by zero
            if speed <= 0:
                speed = 0.1  # Minimum speed to prevent division by zero
            
            # If it's a large exploration movement, allow faster movement
            # This preserves the exploration intent while respecting speed limits
            if dist > speed * 3:  # If movement is much larger than speed (exploration)
                # For exploration, allow faster movement to reach distant targets
                # Use a scaling factor that decreases as distance increases
                exploration_speed_multiplier = min(3.0, 1.0 + (dist / max(speed * 10, 1.0)))
                dx = (dx / dist) * speed * exploration_speed_multiplier
                dy = (dy / dist) * speed * exploration_speed_multiplier
            else:
                # Normal movement: standard normalization
                dx = (dx / dist) * speed
                dy = (dy / dist) * speed
        
        # Apply movement and check for boundary collision
        hit_boundary = animal.move(dx, dy, self.world.environment.width, self.world.environment.height)
        self.spatial_grid.update(animal)
        
        # Handle boundary collisions - when fleeing, direction is already fixed for 3 seconds
        # No need to change direction when hitting boundary during fleeing (direction won't change)
        if hit_boundary and isinstance(animal, (Penguin, Seal, Seagull)):
            if animal.behavior_state == "fleeing":
                # Direction is fixed, just continue (boundary constraint already applied in movement)
                pass
                
            elif animal.behavior_state == "searching":
                # If hit boundary during searching, reverse direction
                animal.hunt_direction_angle = (animal.hunt_direction_angle + math.pi) % (2 * math.pi)
                # Add some randomness to avoid getting stuck
                animal.hunt_direction_angle += random.uniform(-0.5, 0.5)
                # Reset direction timer to continue in new direction
                config = get_config()
                if isinstance(animal, Seagull):
                    animal.hunt_direction_ticks = random.randint(config.SEAGULL_HUNTING_DIRECTION_TICKS_MIN, config.SEAGULL_HUNTING_DIRECTION_TICKS_MAX)
                else:
                    animal.hunt_direction_ticks = random.randint(config.HUNTING_DIRECTION_TICKS_MIN, config.HUNTING_DIRECTION_TICKS_MAX)
    
    def _find_direction_to_nearest_sea(self, x: float, y: float) -> Optional[float]:
        """Find a movement angle that reaches sea with the shortest sampled distance."""
        if not self.world.environment.is_land(x, y):
            return None

        best_angle = None
        best_distance = float('inf')
        angle_samples = 24
        step_distance = 8.0
        max_distance = 240.0

        for i in range(angle_samples):
            angle = (2 * math.pi * i) / angle_samples
            distance = step_distance
            while distance <= max_distance:
                test_x = x + math.cos(angle) * distance
                test_y = y + math.sin(angle) * distance
                if not self.world.environment.is_land(test_x, test_y):
                    if distance < best_distance:
                        best_distance = distance
                        best_angle = angle
                    break
                distance += step_distance

        return best_angle

    def _constrain_direction_near_edge(
        self, 
        animal: Animal, 
        dx: float, 
        dy: float
    ) -> Tuple[float, float]:
        """
        Constrain movement direction when animal is near screen edges.
        
        When an animal is near a map boundary, this method adjusts the
        movement direction to prevent the animal from moving off-screen.
        The direction is constrained to a 180-degree arc facing inward
        from the edge.
        
        For example:
        - Near bottom edge: direction must be between left-to-up-to-right (180°)
        - Near top edge: direction must be between left-to-down-to-right (180°)
        - Near left/right edges: similar constraints apply
        
        Args:
            animal: The animal whose movement is being constrained
            dx: X component of movement direction vector
            dy: Y component of movement direction vector
            
        Returns:
            Tuple[float, float]: Constrained (dx, dy) vector that keeps
                the animal within map boundaries
                
        Note:
            The edge margin is configurable via SimulationConfig.EDGE_MARGIN.
            The method preserves the original movement distance while
            adjusting only the direction.
        """
        config = get_config()
        width = self.world.environment.width
        height = self.world.environment.height
        edge_margin = config.EDGE_MARGIN  # Consider near edge if within this distance
        
        # Check which edge(s) we're near
        near_left = animal.x < edge_margin
        near_right = animal.x > width - edge_margin
        near_top = animal.y < edge_margin
        near_bottom = animal.y > height - edge_margin
        
        # If not near any edge, no constraint needed
        if not (near_left or near_right or near_top or near_bottom):
            return dx, dy
        
        # Calculate current direction angle (0 to 2π, where 0 is right, π/2 is down, π is left, 3π/2 is up)
        current_angle = math.atan2(dy, dx)
        # Normalize to 0-2π range
        if current_angle < 0:
            current_angle += 2 * math.pi
        
        # Store original distance
        original_dist = math.sqrt(dx*dx + dy*dy)
        
        # Constrain angle based on which edge(s) we're near
        # Angle system: 0 = right, π/2 = down, π = left, 3π/2 = up
        
        if near_bottom:
            # Near bottom edge: exclude downward directions (π/2 = down)
            # Allowed: left-to-up-to-right (180°), i.e., exclude π/4 to 3π/4
            if math.pi / 4 < current_angle < 3 * math.pi / 4:
                # Too close to downward, move to nearest allowed direction
                if current_angle < math.pi / 2:
                    current_angle = math.pi / 4  # Move toward right
                else:
                    current_angle = 3 * math.pi / 4  # Move toward left
        
        if near_top:
            # Near top edge: exclude upward directions (3π/2 = up)
            # Allowed: left-to-down-to-right (180°), i.e., exclude 5π/4 to 7π/4
            if 5 * math.pi / 4 < current_angle < 7 * math.pi / 4:
                # Too close to upward, move to nearest allowed direction
                if current_angle < 3 * math.pi / 2:
                    current_angle = 5 * math.pi / 4  # Move toward left
                else:
                    current_angle = 7 * math.pi / 4  # Move toward right
        
        if near_left:
            # Near left edge: exclude leftward directions (π = left)
            # Allowed: up-to-right-to-down (180°), i.e., exclude 3π/4 to 5π/4
            if 3 * math.pi / 4 < current_angle < 5 * math.pi / 4:
                # Too close to leftward, move to nearest allowed direction
                if current_angle < math.pi:
                    current_angle = 3 * math.pi / 4  # Move toward up
                else:
                    current_angle = 5 * math.pi / 4  # Move toward down
        
        if near_right:
            # Near right edge: exclude rightward directions (0 = right, 2π = right)
            # Allowed: up-to-left-to-down (180°), i.e., exclude 7π/4 to 2π and 0 to π/4
            if current_angle > 7 * math.pi / 4 or current_angle < math.pi / 4:
                # Too close to rightward, move to nearest allowed direction
                if current_angle > 7 * math.pi / 4:
                    current_angle = 7 * math.pi / 4  # Move toward up
                elif current_angle < math.pi / 4:
                    current_angle = math.pi / 4  # Move toward down
        
        # Handle corners (near multiple edges) - more restrictive, only allow directions away from both edges
        if near_left and near_top:
            # Top-left corner: only allow down-right (π/4)
            if not (math.pi / 8 < current_angle < 3 * math.pi / 8):
                current_angle = math.pi / 4
        elif near_right and near_top:
            # Top-right corner: only allow down-left (3π/4)
            if not (5 * math.pi / 8 < current_angle < 7 * math.pi / 8):
                current_angle = 3 * math.pi / 4
        elif near_left and near_bottom:
            # Bottom-left corner: only allow up-right (7π/4)
            if not (current_angle > 13 * math.pi / 8 or current_angle < math.pi / 8):
                current_angle = 7 * math.pi / 4
        elif near_right and near_bottom:
            # Bottom-right corner: only allow up-left (5π/4)
            if not (9 * math.pi / 8 < current_angle < 11 * math.pi / 8):
                current_angle = 5 * math.pi / 4
        
        # Recalculate dx, dy from constrained angle, preserving original distance
        dx = math.cos(current_angle) * original_dist
        dy = math.sin(current_angle) * original_dist
        
        return dx, dy

    def _drop_seagull_fish(self, seagull: Seagull):
        """Drop a carried fish on current floe position."""
        if not seagull.carrying_fish:
            return
        config = get_config()
        dropped = FloeFish(
            id=f"floe_fish_{self.world.tick}_{random.randint(1000, 9999)}",
            x=seagull.x,
            y=seagull.y,
            ttl_ticks=config.SEAGULL_PREY_DROP_TTL_TICKS,
        )
        self.world.floe_fish.append(dropped)
        seagull.carrying_fish = False
        seagull.prey_processing_ticks = 0
        seagull.target_id = ""

    def _find_nearest_floe_fish(self, animal: Animal, max_distance: float) -> Optional[FloeFish]:
        """Find nearest dropped floe fish within range."""
        nearest = None
        min_dist = max_distance
        for floe_fish in self.world.floe_fish:
            if not floe_fish.is_available():
                continue
            dist = math.sqrt((animal.x - floe_fish.x) ** 2 + (animal.y - floe_fish.y) ** 2)
            if dist < min_dist:
                min_dist = dist
                nearest = floe_fish
        return nearest

    def _find_nearest_feeding_seagull(self, animal: Animal, max_distance: float) -> Optional[Seagull]:
        """Find nearest grounded seagull that is actively processing prey."""
        nearest = None
        min_dist = max_distance
        for seagull in self.world.seagulls:
            if not seagull.is_alive():
                continue
            if seagull.state != "grounded":
                continue
            if seagull.behavior_state != "processing_prey":
                continue
            if not seagull.carrying_fish:
                continue
            dist = animal.distance_to(seagull)
            if dist < min_dist:
                min_dist = dist
                nearest = seagull
        return nearest

    def _find_nearest_land_food_source(self, animal: Animal, max_distance: float):
        """Return nearest land food source: dropped fish or feeding seagull."""
        floe_fish = self._find_nearest_floe_fish(animal, max_distance=max_distance)
        feeding_seagull = self._find_nearest_feeding_seagull(animal, max_distance=max_distance)

        if floe_fish is None:
            return feeding_seagull
        if feeding_seagull is None:
            return floe_fish

        fish_dist = math.sqrt((animal.x - floe_fish.x) ** 2 + (animal.y - floe_fish.y) ** 2)
        seagull_dist = animal.distance_to(feeding_seagull)
        return floe_fish if fish_dist <= seagull_dist else feeding_seagull
    
    def _find_nearest(
        self, 
        animal: Animal, 
        targets: List[Animal], 
        max_distance: float = float('inf')
    ) -> Optional[Animal]:
        """
        Find the nearest target animal within a specified distance.
        
        Searches through a list of target animals and returns the one
        closest to the given animal, if it's within max_distance.
        
        Args:
            animal: The animal to find nearest target for
            targets: List of potential target animals
            max_distance: Maximum distance to search (default: unlimited)
            
        Returns:
            Optional[Animal]: The nearest target within range, or None if
                no target is found within max_distance
                
        Note:
            Only considers alive animals. Dead animals are automatically
            skipped in the search. Uses spatial grid for optimization when
            max_distance is specified.
        """
        # Use spatial grid optimization if max_distance is limited
        if max_distance < float('inf') and targets:
            nearest = self.spatial_grid.find_nearest(
                animal.x,
                animal.y,
                targets,
                max_distance=max_distance,
                exclude=animal
            )
            if nearest is not None:
                return nearest
        
        # Fallback to linear search for unlimited distance
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
        # Seals eat penguins (both in sea and on land/ice floes)
        # Seals can hunt penguins anywhere they meet
        for seal in self.world.seals[:]:
            if not seal.is_alive():
                continue
            
            for penguin in self.world.penguins[:]:
                if not penguin.is_alive():
                    continue
                
                # Seals can hunt penguins in the same location (both in sea or both on land)
                if seal.state != penguin.state:
                    continue
                
                if seal.distance_to(penguin) < 10:
                    # Predation successful
                    config = get_config()
                    # Seals get more energy from eating penguins than fish
                    seal.gain_energy(config.SEAL_ENERGY_RECOVERY_FISH * 2)
                    # Remove from spatial grid before removing from world
                    self.spatial_grid.remove(penguin)
                    self.world.penguins.remove(penguin)
                    # Set hunting cooldown (10 seconds at 5 ticks/sec)
                    config = get_config()
                    seal.hunting_cooldown = config.HUNTING_COOLDOWN_TICKS
                    # Update behavior state after successful predation
                    # Clear target ID if in targeting state
                    if seal.behavior_state == "targeting":
                        seal.target_id = ""  # Clear target ID
                    # Exit hunting states (searching or targeting) due to cooldown
                    if seal.behavior_state in ["searching", "targeting"]:
                        energy_percent = seal.energy / seal.max_energy
                        # Can't enter searching state during cooldown
                        seal.behavior_state = "idle"
                        seal.hunt_direction_ticks = 0
                    break

        # Penguins/Seals scavenge fish dropped on ice floes while searching on land.
        for floe_fish in self.world.floe_fish[:]:
            eaten = False

            for penguin in self.world.penguins[:]:
                if not penguin.is_alive() or penguin.state != "land" or penguin.behavior_state != "searching":
                    continue
                if math.sqrt((penguin.x - floe_fish.x) ** 2 + (penguin.y - floe_fish.y) ** 2) < 6:
                    config = get_config()
                    penguin.gain_energy(config.PENGUIN_ENERGY_RECOVERY_FISH)
                    penguin.hunting_cooldown = config.HUNTING_COOLDOWN_TICKS
                    penguin.behavior_state = "idle"
                    penguin.hunt_direction_ticks = 0
                    self.world.floe_fish.remove(floe_fish)
                    eaten = True
                    break

            if eaten:
                continue

            for seal in self.world.seals[:]:
                if not seal.is_alive() or seal.state != "land" or seal.behavior_state != "searching":
                    continue
                if math.sqrt((seal.x - floe_fish.x) ** 2 + (seal.y - floe_fish.y) ** 2) < 8:
                    config = get_config()
                    seal.gain_energy(config.SEAL_ENERGY_RECOVERY_FISH)
                    seal.hunting_cooldown = config.HUNTING_COOLDOWN_TICKS
                    seal.behavior_state = "idle"
                    seal.hunt_direction_ticks = 0
                    self.world.floe_fish.remove(floe_fish)
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
                    config = get_config()
                    seal.gain_energy(config.SEAL_ENERGY_RECOVERY_FISH)
                    # Remove from spatial grid before removing from world
                    self.spatial_grid.remove(fish)
                    self.world.fish.remove(fish)
                    # Set hunting cooldown (10 seconds at 5 ticks/sec)
                    config = get_config()
                    seal.hunting_cooldown = config.HUNTING_COOLDOWN_TICKS
                    # Update behavior state after successful predation
                    # Clear target ID if in targeting state
                    if seal.behavior_state == "targeting":
                        seal.target_id = ""  # Clear target ID
                    # Exit hunting states (searching or targeting) due to cooldown
                    if seal.behavior_state in ["searching", "targeting"]:
                        energy_percent = seal.energy / seal.max_energy
                        # Can't enter searching state during cooldown
                        seal.behavior_state = "idle"
                        seal.hunt_direction_ticks = 0
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
                    config = get_config()
                    penguin.gain_energy(config.PENGUIN_ENERGY_RECOVERY_FISH)
                    # Remove from spatial grid before removing from world
                    self.spatial_grid.remove(fish)
                    self.world.fish.remove(fish)
                    # Set hunting cooldown (10 seconds at 5 ticks/sec)
                    penguin.hunting_cooldown = config.HUNTING_COOLDOWN_TICKS
                    # Update behavior state after successful predation
                    # Clear target ID if in targeting state
                    if penguin.behavior_state == "targeting":
                        penguin.target_id = ""  # Clear target ID
                    # Exit hunting states (searching or targeting) due to cooldown
                    if penguin.behavior_state in ["searching", "targeting"]:
                        energy_percent = penguin.energy / penguin.max_energy
                        # Can't enter searching state during cooldown
                        penguin.behavior_state = "idle"
                        penguin.hunt_direction_ticks = 0
                    break

        # Seagulls catch fish in sea, then must carry prey to ice floe before eating.
        for seagull in self.world.seagulls[:]:
            if not seagull.is_alive() or seagull.carrying_fish or seagull.state != "flying":
                continue
            for fish in self.world.fish[:]:
                if not fish.is_alive():
                    continue
                if seagull.distance_to(fish) < 8:
                    self.spatial_grid.remove(fish)
                    self.world.fish.remove(fish)
                    seagull.carrying_fish = True
                    seagull.prey_processing_ticks = 0
                    seagull.behavior_state = "carrying_to_land"
                    seagull.target_id = ""
                    seagull.hunt_direction_ticks = 0
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
                    # Add to spatial grid
                    self.spatial_grid.add(baby)
        
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
                    # Add to spatial grid
                    self.spatial_grid.add(baby)
        
        # Seagulls breed (only when grounded on ice floe)
        breeding_seagulls = [
            g for g in self.world.seagulls
            if g.can_breed() and g.state == "grounded" and self.world.environment.is_land(g.x, g.y)
        ]
        if len(breeding_seagulls) >= 2:
            random.shuffle(breeding_seagulls)
            for i in range(0, len(breeding_seagulls) - 1, 2):
                g1, g2 = breeding_seagulls[i], breeding_seagulls[i + 1]
                if g1.distance_to(g2) < 25:
                    baby = g1.breed()
                    g2.breeding_cooldown = g2.max_breeding_cooldown
                    g2.consume_energy(35)
                    baby.state = "grounded"
                    baby.last_x = baby.x
                    baby.last_y = baby.y
                    self.world.seagulls.append(baby)
                    self.spatial_grid.add(baby)

        # Fish breed (in the sea)
        breeding_fish = [f for f in self.world.fish if f.is_alive() and f.energy > 30]
        if len(breeding_fish) >= 2 and random.random() < 0.1:  # 10% breeding probability
            random.shuffle(breeding_fish)
            for i in range(0, min(5, len(breeding_fish) - 1), 2):  # Max 5 pairs
                f1, f2 = breeding_fish[i], breeding_fish[i + 1]
                if f1.distance_to(f2) < 10:
                    baby = f1.breed()
                    # Check if baby position is on land, if so find a nearby sea position
                    if self.world.environment.is_land(baby.x, baby.y):
                        # Find a nearby sea position (try positions around parent first)
                        sea_x, sea_y = self._find_sea_position()
                        # Try to keep it close to parent if possible
                        for attempt in range(10):
                            offset_x = random.uniform(-20, 20)
                            offset_y = random.uniform(-20, 20)
                            test_x = f1.x + offset_x
                            test_y = f1.y + offset_y
                            if 0 <= test_x < self.world.environment.width and \
                               0 <= test_y < self.world.environment.height and \
                               not self.world.environment.is_land(test_x, test_y):
                                sea_x, sea_y = test_x, test_y
                                break
                        baby.x = sea_x
                        baby.y = sea_y
                    f1.consume_energy(10)
                    f2.consume_energy(10)
                    self.world.fish.append(baby)
                    # Add to spatial grid
                    self.spatial_grid.add(baby)
    
    def _remove_dead_animals(self):
        """
        Remove dead animals from the world and spatial grid.
        
        Animals are considered dead if:
        - Energy <= 0 (starvation)
        - Age >= max_age (natural death from old age)
        """
        # Remove dead penguins
        dead_penguins = [p for p in self.world.penguins if not p.is_alive()]
        for penguin in dead_penguins:
            self.spatial_grid.remove(penguin)
        self.world.penguins = [p for p in self.world.penguins if p.is_alive()]
        
        # Remove dead seals
        dead_seals = [s for s in self.world.seals if not s.is_alive()]
        for seal in dead_seals:
            self.spatial_grid.remove(seal)
        self.world.seals = [s for s in self.world.seals if s.is_alive()]
        
        # Remove dead fish
        dead_fish = [f for f in self.world.fish if not f.is_alive()]
        for fish in dead_fish:
            self.spatial_grid.remove(fish)
        self.world.fish = [f for f in self.world.fish if f.is_alive()]

        # Remove dead seagulls
        dead_seagulls = [g for g in self.world.seagulls if not g.is_alive()]
        for seagull in dead_seagulls:
            self.spatial_grid.remove(seagull)
        self.world.seagulls = [g for g in self.world.seagulls if g.is_alive()]

        # Remove expired floe fish
        self.world.floe_fish = [f for f in self.world.floe_fish if f.is_available()]
    
    def get_state(self) -> WorldState:
        """
        Get the current world state.
        
        Returns:
            WorldState: The complete current state of the simulation,
                including all animals, environment, and tick count.
                
        Note:
            This returns a reference to the internal world state.
            Modifying the returned object will affect the simulation.
            For serialization, use `state.to_dict()` instead.
        """
        return self.world
    
    def step(self, n: int = 1):
        """
        Advance the simulation by N steps.
        
        Executes the tick() method N times, effectively advancing
        the simulation by N time steps.
        
        Args:
            n: Number of steps to advance (default: 1)
            
        Example:
            ```python
            engine = SimulationEngine()
            engine.step(100)  # Advance 100 ticks
            state = engine.get_state()
            print(f"Current tick: {state.tick}")  # Should be 100
            ```
        """
        for _ in range(n):
            self.tick()
