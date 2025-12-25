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
            penguin = Penguin(
                id=f"penguin_{i}",
                x=random.uniform(0, self.world.environment.width * 0.3),
                y=random.uniform(0, self.world.environment.height),
                energy=random.uniform(50, 100),
                state="land"
            )
            # Initialize position tracking for boundary detection
            penguin.last_x = penguin.x
            penguin.last_y = penguin.y
            self.world.penguins.append(penguin)
        
        # Create initial seals (in the sea)
        for i in range(5):
            seal = Seal(
                id=f"seal_{i}",
                x=random.uniform(self.world.environment.width * 0.5, self.world.environment.width),
                y=random.uniform(0, self.world.environment.height),
                energy=random.uniform(80, 150),
                state="sea"
            )
            # Initialize position tracking for boundary detection
            seal.last_x = seal.x
            seal.last_y = seal.y
            self.world.seals.append(seal)
        
        # Create initial fish (in the sea, not on ice floes)
        for i in range(50):
            # Find a position in the sea (not on any ice floe)
            x, y = self._find_sea_position()
            self.world.fish.append(
                Fish(
                    id=f"fish_{i}",
                    x=x,
                    y=y,
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
    
    def _find_sea_position(self, max_attempts: int = 50):
        """Find a random position in the sea (not on any ice floe)"""
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
        # Ensure minimum fish population
        if len(self.world.fish) < 20:
            if random.random() < 0.1: # 10% chance per tick to spawn a fish if low
                # Find a position in the sea (not on any ice floe)
                x, y = self._find_sea_position()
                self.world.fish.append(
                    Fish(
                        id=f"fish_spawn_{self.world.tick}_{random.randint(100,999)}",
                        x=x,
                        y=y,
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
        
        # 1b. Social behavior (分散) - only when not fleeing or targeting
        # Priority: 逃跑 > 锁定 > 分散 > 捕食
        if isinstance(animal, (Penguin, Seal)) and dx == 0 and dy == 0 and \
           animal.behavior_state not in ["fleeing", "targeting"]:
            energy_percent = animal.energy / animal.max_energy
            has_energy_for_social = energy_percent > 0.6  # Only socialize when energy > 60%
            
            if is_on_land:
                # On land: Social behavior depends on energy level
                same_type = [p for p in self.world.penguins if isinstance(animal, Penguin) and p.id != animal.id and p.is_alive() and p.state == "land"]
                if isinstance(animal, Seal):
                    same_type = [s for s in self.world.seals if s.id != animal.id and s.is_alive() and s.state == "land"]
                
                if same_type:
                    nearby = [a for a in same_type if animal.distance_to(a) < 50]
                    if nearby:
                        if has_energy_for_social:
                            # Energy > 60%: Social grouping behavior (抱团)
                            # If too crowded (more than 3 nearby), move away slightly
                            if len(nearby) > 3:
                                # Move away from center of nearby animals
                                center_x = sum(a.x for a in nearby) / len(nearby)
                                center_y = sum(a.y for a in nearby) / len(nearby)
                                dx = animal.x - center_x
                                dy = animal.y - center_y
                                # Ensure meaningful movement
                                if abs(dx) < 5 and abs(dy) < 5:
                                    # Too small, add random component
                                    dx += random.uniform(-20, 20)
                                    dy += random.uniform(-20, 20)
                            else:
                                # Move towards a nearby animal (social grouping - 抱团)
                                target_animal = random.choice(nearby)
                                dx = target_animal.x - animal.x
                                dy = target_animal.y - animal.y
                                # Make movement subtle for gentle grouping
                                if abs(dx) < 3 and abs(dy) < 3:
                                    # Very close, add small exploration component
                                    angle = random.uniform(0, 2 * math.pi)
                                    dx += math.cos(angle) * 10
                                    dy += math.sin(angle) * 10
                        else:
                            # Energy ≤ 60%: Dispersal behavior (分散，不抱团)
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
                # In sea: Always active dispersal behavior (分散觅食)
                # Avoid clustering with same type animals to spread out for foraging
                same_type = [p for p in self.world.penguins if isinstance(animal, Penguin) and p.id != animal.id and p.is_alive() and p.state == "sea"]
                if isinstance(animal, Seal):
                    same_type = [s for s in self.world.seals if s.id != animal.id and s.is_alive() and s.state == "sea"]
                
                if same_type:
                    # Find nearby animals of same type
                    nearby = [a for a in same_type if animal.distance_to(a) < 80]
                    if nearby:
                        # Move away from nearby animals to disperse (分散)
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
        
        # 1.5. Update behavior state based on energy
        # Enter searching mode when energy drops below 60%
        if isinstance(animal, (Penguin, Seal)):
            energy_percent = animal.energy / animal.max_energy
            # Only change to searching if not fleeing or targeting
            if energy_percent < 0.6 and animal.behavior_state not in ["fleeing", "targeting"]:
                if animal.behavior_state != "searching":
                    animal.behavior_state = "searching"  # 搜寻状态
                    # Initialize searching direction when entering searching mode
                    animal.hunt_direction_angle = random.uniform(0, 2 * math.pi)
                    animal.hunt_direction_ticks = random.randint(15, 40)
            elif energy_percent >= 0.6 and animal.behavior_state == "searching":
                animal.behavior_state = "idle"
                animal.hunt_direction_ticks = 0
        
        # 2. Safety (Avoid Predators) - High Priority override
        # Penguins should flee from Seals
        if isinstance(animal, Penguin):
            predators = [s for s in self.world.seals if s.is_alive()]
            # Perception range depends on location: smaller on land, larger in sea
            # On land, penguins have reduced awareness (harder to detect seals)
            # In sea, penguins have better awareness (easier to detect seals)
            if is_on_land:
                perception_range = 60  # Reduced perception on land (60 units instead of 150)
            else:
                perception_range = 150  # Normal perception in sea
            nearest_predator = self._find_nearest(animal, predators, max_distance=perception_range)
            
            if nearest_predator:
                # Flee! Change to fleeing state (最高优先级: 逃跑 > 锁定 > 分散 > 捕食)
                animal.behavior_state = "fleeing"
                
                # Calculate base fleeing direction (away from predator)
                base_dx = animal.x - nearest_predator.x
                base_dy = animal.y - nearest_predator.y
                base_flee_angle = math.atan2(base_dy, base_dx) if (base_dx != 0 or base_dy != 0) else random.uniform(0, 2 * math.pi)
                
                # Check for ice floes in the fleeing direction (前方不远处)
                # Look for ice floes within 200 units in the fleeing direction
                ice_floe_found = None
                min_floe_distance = float('inf')
                
                for floe in self.world.environment.ice_floes:
                    # Calculate distance to floe
                    floe_dx = floe['x'] - animal.x
                    floe_dy = floe['y'] - animal.y
                    floe_distance = math.sqrt(floe_dx**2 + floe_dy**2)
                    
                    # Check if floe is in front (within 60 degrees of fleeing direction)
                    if floe_distance > 0 and floe_distance < 200:  # Within 200 units
                        floe_angle = math.atan2(floe_dy, floe_dx)
                        angle_diff = abs((floe_angle - base_flee_angle + math.pi) % (2 * math.pi) - math.pi)
                        
                        # If floe is in front (within 60 degrees) and closer than previous
                        if angle_diff < math.pi / 3 and floe_distance < min_floe_distance:
                            ice_floe_found = floe
                            min_floe_distance = floe_distance
                
                # If found ice floe in front, flee towards it (冲向浮冰)
                if ice_floe_found:
                    dx = ice_floe_found['x'] - animal.x
                    dy = ice_floe_found['y'] - animal.y
                    animal.flee_edge_direction = math.atan2(dy, dx)
                    # Set timer to continue towards floe
                    animal.hunt_direction_ticks = random.randint(15, 30)
                else:
                    # No ice floe found, use base fleeing direction
                    dx = base_dx
                    dy = base_dy
                    animal.flee_edge_direction = base_flee_angle
                    animal.hunt_direction_ticks = 0
                
                target = nearest_predator # Just to mark as "busy" so we don't hunt while fleeing
            elif animal.behavior_state == "fleeing":
                # Continue fleeing even if predator not visible (maintain fleeing state briefly)
                # Check if we should look for ice floes while fleeing
                if animal.hunt_direction_ticks > 0:
                    # Continue in current direction (towards floe or along edge)
                    animal.hunt_direction_ticks -= 1
                    dx = math.cos(animal.flee_edge_direction) * 30
                    dy = math.sin(animal.flee_edge_direction) * 30
                else:
                    # Check for nearby ice floes to escape to
                    ice_floe_found = None
                    min_floe_distance = float('inf')
                    
                    for floe in self.world.environment.ice_floes:
                        floe_dx = floe['x'] - animal.x
                        floe_dy = floe['y'] - animal.y
                        floe_distance = math.sqrt(floe_dx**2 + floe_dy**2)
                        
                        # Look for nearby ice floes (within 150 units)
                        if floe_distance > 0 and floe_distance < 150:
                            if floe_distance < min_floe_distance:
                                ice_floe_found = floe
                                min_floe_distance = floe_distance
                    
                    if ice_floe_found:
                        # Head towards ice floe
                        dx = ice_floe_found['x'] - animal.x
                        dy = ice_floe_found['y'] - animal.y
                        animal.flee_edge_direction = math.atan2(dy, dx)
                        animal.hunt_direction_ticks = random.randint(15, 30)
                    else:
                        # No ice floe found, continue fleeing or exit fleeing state
                        # No longer see predator, can resume searching if low energy
                        energy_percent = animal.energy / animal.max_energy
                        if energy_percent < 0.6:
                            animal.behavior_state = "searching"  # 返回搜寻状态
                            # Initialize new searching direction
                            animal.hunt_direction_angle = random.uniform(0, 2 * math.pi)
                            animal.hunt_direction_ticks = random.randint(15, 40)
                        else:
                            animal.behavior_state = "idle"
                            animal.hunt_direction_ticks = 0
        
        # 3. Searching Behavior (搜寻状态) - when energy < 60%
        # Animals move in a direction for 3-8 seconds (15-40 ticks at 5 ticks/sec), then change direction
        # If they find food or hit boundary, change behavior
        if not target and isinstance(animal, (Penguin, Seal)) and animal.behavior_state == "searching":
            # Check if we need to set a new searching direction
            if animal.hunt_direction_ticks <= 0:
                # Set new random direction (3-8 seconds = 15-40 ticks at 5 ticks/sec)
                animal.hunt_direction_ticks = random.randint(15, 40)
                animal.hunt_direction_angle = random.uniform(0, 2 * math.pi)
            
            # Decrease direction timer
            animal.hunt_direction_ticks -= 1
            
            # Move in the searching direction
            search_distance = 30 + random.uniform(0, 20)  # 30-50 units per step
            dx = math.cos(animal.hunt_direction_angle) * search_distance
            dy = math.sin(animal.hunt_direction_angle) * search_distance
            
            # Check for prey while searching
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
                
                valid_prey = [
                    p for p in potential_prey 
                    if p.is_alive() and p != animal and 
                    (isinstance(p, Fish) or p.state == animal.state)
                ]
                
                # Look for nearby prey (within 200 units)
                nearby_prey = self._find_nearest(animal, valid_prey, max_distance=200)
                if nearby_prey:
                    # Found prey! Switch from searching to targeting (锁定状态)
                    animal.behavior_state = "targeting"  # 锁定状态
                    animal.target_id = nearby_prey.id  # Store target ID for tracking
                    target = nearby_prey
                    dx = nearby_prey.x - animal.x
                    dy = nearby_prey.y - animal.y
                    # Reset direction timer
                    animal.hunt_direction_ticks = 0
        
        # 3a. Targeting prey (锁定状态) - when found prey during searching
        if not target and isinstance(animal, (Penguin, Seal)) and animal.behavior_state == "targeting":
            # Continue targeting - look for the prey we were chasing
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
                    max_tracking_distance = 400  # Maximum distance before giving up
                    
                    if distance_to_target <= max_tracking_distance:
                        # Target is still within range, continue tracking
                        target = tracked_prey
                        dx = tracked_prey.x - animal.x
                        dy = tracked_prey.y - animal.y
                    else:
                        # Target is too far away, give up tracking
                        animal.target_id = ""  # Clear target ID
                        energy_percent = animal.energy / animal.max_energy
                        if energy_percent < 0.6:
                            animal.behavior_state = "searching"  # 返回搜寻状态
                            animal.hunt_direction_angle = random.uniform(0, 2 * math.pi)
                            animal.hunt_direction_ticks = random.randint(15, 40)
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
                        animal.target_id = ""  # Clear target ID
                        energy_percent = animal.energy / animal.max_energy
                        if energy_percent < 0.6:
                            animal.behavior_state = "searching"  # 返回搜寻状态
                            animal.hunt_direction_angle = random.uniform(0, 2 * math.pi)
                            animal.hunt_direction_ticks = random.randint(15, 40)
                        else:
                            animal.behavior_state = "idle"
                            animal.hunt_direction_ticks = 0
        
        # 3b. Regular Hunting (when not in searching/targeting mode, but still looking for food)
        # Penguins and Seals actively hunt even when not very hungry to explore and find food
        if not target and isinstance(animal, (Penguin, Seal)) and animal.behavior_state not in ["searching", "targeting"]:
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
                
                # Increased search range for better exploration (600 instead of 300)
                target = self._find_nearest(animal, valid_prey, max_distance=600)
                if target:
                    dx = target.x - animal.x
                    dy = target.y - animal.y
        
        # 4. Active Exploration (if no other drive, for Penguins and Seals)
        # Instead of small random movements, make them explore larger areas
        if dx == 0 and dy == 0:
            if isinstance(animal, (Penguin, Seal)):
                # Active exploration: move towards unexplored areas
                # On land, explore the ice floe; in sea, explore the ocean
                if is_on_land:
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
                    # In sea: explore larger areas
                    exploration_distance = 50 + random.uniform(0, 100)  # 50-150 units
                    angle = random.uniform(0, 2 * math.pi)
                    dx = math.cos(angle) * exploration_distance
                    dy = math.sin(angle) * exploration_distance
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
        
        # Handle boundary collisions based on behavior state
        if hit_boundary and isinstance(animal, (Penguin, Seal)):
            if animal.behavior_state == "fleeing":
                # When fleeing and hit boundary, move along the edge
                # Determine which edge was hit and choose direction along it
                width = self.world.environment.width
                height = self.world.environment.height
                edge_margin = 5  # Consider near edge if within this distance
                
                # Check which edge(s) we're near
                near_left = animal.x < edge_margin
                near_right = animal.x > width - edge_margin
                near_top = animal.y < edge_margin
                near_bottom = animal.y > height - edge_margin
                
                # Choose direction along the edge
                if near_left or near_right:
                    # On vertical edge, move along vertically (up or down)
                    if near_top:
                        # Top-left or top-right corner, move down
                        animal.flee_edge_direction = math.pi / 2  # Down
                    elif near_bottom:
                        # Bottom-left or bottom-right corner, move up
                        animal.flee_edge_direction = -math.pi / 2  # Up
                    else:
                        # Middle of vertical edge, random up or down
                        animal.flee_edge_direction = random.choice([math.pi / 2, -math.pi / 2])
                elif near_top or near_bottom:
                    # On horizontal edge, move along horizontally (left or right)
                    if near_left:
                        # Top-left or bottom-left corner, move right
                        animal.flee_edge_direction = 0  # Right
                    elif near_right:
                        # Top-right or bottom-right corner, move left
                        animal.flee_edge_direction = math.pi  # Left
                    else:
                        # Middle of horizontal edge, random left or right
                        animal.flee_edge_direction = random.choice([0, math.pi])
                else:
                    # Near corner, pick a direction along one of the edges
                    if near_left and near_top:
                        animal.flee_edge_direction = random.choice([0, math.pi / 2])  # Right or Down
                    elif near_left and near_bottom:
                        animal.flee_edge_direction = random.choice([0, -math.pi / 2])  # Right or Up
                    elif near_right and near_top:
                        animal.flee_edge_direction = random.choice([math.pi, math.pi / 2])  # Left or Down
                    elif near_right and near_bottom:
                        animal.flee_edge_direction = random.choice([math.pi, -math.pi / 2])  # Left or Up
                    else:
                        # Default: random direction
                        animal.flee_edge_direction = random.uniform(0, 2 * math.pi)
                
                # Set timer to continue along edge
                animal.hunt_direction_ticks = random.randint(20, 40)
                
            elif animal.behavior_state == "searching":
                # If hit boundary during searching, reverse direction
                animal.hunt_direction_angle = (animal.hunt_direction_angle + math.pi) % (2 * math.pi)
                # Add some randomness to avoid getting stuck
                animal.hunt_direction_angle += random.uniform(-0.5, 0.5)
                # Reset direction timer to continue in new direction
                animal.hunt_direction_ticks = random.randint(15, 40)
    
    def _constrain_direction_near_edge(self, animal, dx: float, dy: float):
        """Constrain movement direction when near screen edges
        
        If animal is near an edge, limit movement direction to 180 degrees facing inward.
        For example, if near bottom edge, direction must be between left-to-up-to-right (180°).
        
        Args:
            animal: The animal to check
            dx, dy: Movement direction vector
            
        Returns:
            Constrained dx, dy
        """
        width = self.world.environment.width
        height = self.world.environment.height
        edge_margin = 50  # Consider near edge if within this distance
        
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
                    # Update behavior state after successful predation
                    if seal.behavior_state == "targeting":
                        seal.target_id = ""  # Clear target ID
                        energy_percent = seal.energy / seal.max_energy
                        if energy_percent < 0.6:
                            seal.behavior_state = "searching"  # 返回搜寻状态
                            seal.hunt_direction_angle = random.uniform(0, 2 * math.pi)
                            seal.hunt_direction_ticks = random.randint(15, 40)
                        else:
                            seal.behavior_state = "idle"
                            seal.hunt_direction_ticks = 0
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
                    # Update behavior state after successful predation
                    if seal.behavior_state == "targeting":
                        seal.target_id = ""  # Clear target ID
                        energy_percent = seal.energy / seal.max_energy
                        if energy_percent < 0.6:
                            seal.behavior_state = "searching"  # 返回搜寻状态
                            seal.hunt_direction_angle = random.uniform(0, 2 * math.pi)
                            seal.hunt_direction_ticks = random.randint(15, 40)
                        else:
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
                    penguin.gain_energy(15)
                    self.world.fish.remove(fish)
                    # Update behavior state after successful predation
                    if penguin.behavior_state == "targeting":
                        penguin.target_id = ""  # Clear target ID
                        energy_percent = penguin.energy / penguin.max_energy
                        if energy_percent < 0.6:
                            penguin.behavior_state = "searching"  # 返回搜寻状态
                            penguin.hunt_direction_angle = random.uniform(0, 2 * math.pi)
                            penguin.hunt_direction_ticks = random.randint(15, 40)
                        else:
                            penguin.behavior_state = "idle"
                            penguin.hunt_direction_ticks = 0
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

