"""
Spatial partitioning system for efficient neighbor queries.

This module implements a grid-based spatial partitioning system to optimize
the O(n) linear search for finding nearest neighbors. Instead of checking
all animals, we only check animals in nearby grid cells.
"""
from typing import List, Dict, Tuple, Optional, Set
from .animals import Animal
import math


class SpatialGrid:
    """
    Grid-based spatial partitioning for efficient spatial queries.
    
    Divides the world into a grid of cells. Each animal is stored in the
    cell corresponding to its position. When searching for neighbors, we
    only need to check the current cell and adjacent cells.
    
    This reduces the time complexity from O(n) to approximately O(k) where
    k is the average number of animals per cell (typically much smaller than n).
    
    Attributes:
        cell_size (float): Size of each grid cell
        width (int): World width
        height (int): World height
        cols (int): Number of columns in the grid
        rows (int): Number of rows in the grid
        grid (Dict[Tuple[int, int], List[Animal]]): Grid cells containing animals
    """
    
    def __init__(self, width: int, height: int, cell_size: float = 100.0):
        """
        Initialize spatial grid.
        
        Args:
            width: World width in pixels
            height: World height in pixels
            cell_size: Size of each grid cell (default: 100 pixels)
                Smaller cells = more precise but more cells to check
                Larger cells = fewer cells but less precise
        """
        self.cell_size = cell_size
        self.width = width
        self.height = height
        self.cols = int(math.ceil(width / cell_size))
        self.rows = int(math.ceil(height / cell_size))
        # Grid: (col, row) -> List[Animal]
        self.grid: Dict[Tuple[int, int], List[Animal]] = {}
        # Track which animals are in which cells for fast removal
        # Use animal.id as key since Animal objects are not hashable
        self._animal_cells: Dict[str, Set[Tuple[int, int]]] = {}
    
    def _get_cell(self, x: float, y: float) -> Tuple[int, int]:
        """
        Get grid cell coordinates for a position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Tuple[int, int]: (col, row) cell coordinates
        """
        col = int(x / self.cell_size)
        row = int(y / self.cell_size)
        # Clamp to valid range
        col = max(0, min(col, self.cols - 1))
        row = max(0, min(row, self.rows - 1))
        return (col, row)
    
    def add(self, animal: Animal):
        """
        Add an animal to the spatial grid.
        
        Args:
            animal: Animal to add
        """
        cell = self._get_cell(animal.x, animal.y)
        if cell not in self.grid:
            self.grid[cell] = []
        if animal not in self.grid[cell]:
            self.grid[cell].append(animal)
        
        # Track which cells this animal is in (use id as key)
        if animal.id not in self._animal_cells:
            self._animal_cells[animal.id] = set()
        self._animal_cells[animal.id].add(cell)
    
    def remove(self, animal: Animal):
        """
        Remove an animal from the spatial grid.
        
        Args:
            animal: Animal to remove
        """
        if animal.id in self._animal_cells:
            for cell in self._animal_cells[animal.id]:
                if cell in self.grid and animal in self.grid[cell]:
                    self.grid[cell].remove(animal)
                    # Clean up empty cells
                    if not self.grid[cell]:
                        del self.grid[cell]
            del self._animal_cells[animal.id]
    
    def update(self, animal: Animal):
        """
        Update animal position in the grid.
        
        This should be called when an animal moves. The animal will be
        moved to the appropriate cell if it has crossed cell boundaries.
        
        Args:
            animal: Animal whose position has changed
        """
        new_cell = self._get_cell(animal.x, animal.y)
        
        # Check if animal needs to be moved to a different cell
        if animal.id in self._animal_cells:
            old_cells = self._animal_cells[animal.id].copy()
            for old_cell in old_cells:
                if old_cell != new_cell:
                    # Remove from old cell
                    if old_cell in self.grid and animal in self.grid[old_cell]:
                        self.grid[old_cell].remove(animal)
                        if not self.grid[old_cell]:
                            del self.grid[old_cell]
                    self._animal_cells[animal.id].discard(old_cell)
        
        # Add to new cell
        if new_cell not in self.grid:
            self.grid[new_cell] = []
        if animal not in self.grid[new_cell]:
            self.grid[new_cell].append(animal)
        
        if animal.id not in self._animal_cells:
            self._animal_cells[animal.id] = set()
        self._animal_cells[animal.id].add(new_cell)
    
    def get_nearby_cells(self, x: float, y: float, radius: float) -> List[Tuple[int, int]]:
        """
        Get all grid cells within a radius of a position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            radius: Search radius
            
        Returns:
            List[Tuple[int, int]]: List of (col, row) cell coordinates to check
        """
        center_cell = self._get_cell(x, y)
        # Calculate how many cells to check in each direction
        cells_radius = int(math.ceil(radius / self.cell_size)) + 1
        
        nearby_cells = []
        for dc in range(-cells_radius, cells_radius + 1):
            for dr in range(-cells_radius, cells_radius + 1):
                col = center_cell[0] + dc
                row = center_cell[1] + dr
                # Check bounds
                if 0 <= col < self.cols and 0 <= row < self.rows:
                    nearby_cells.append((col, row))
        
        return nearby_cells
    
    def get_nearby_animals(
        self, 
        x: float, 
        y: float, 
        radius: float,
        exclude: Optional[Animal] = None,
        filter_func: Optional[callable] = None
    ) -> List[Animal]:
        """
        Get all animals within a radius of a position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            radius: Search radius
            exclude: Animal to exclude from results (typically the searching animal)
            filter_func: Optional function to filter animals (e.g., lambda a: a.is_alive())
            
        Returns:
            List[Animal]: List of animals within radius
        """
        nearby_cells = self.get_nearby_cells(x, y, radius)
        candidates: List[Animal] = []
        seen: Set[str] = set()  # Use animal.id instead of animal object
        
        # Collect candidates from nearby cells
        for cell in nearby_cells:
            if cell in self.grid:
                for animal in self.grid[cell]:
                    if animal.id not in seen:
                        seen.add(animal.id)
                        # Apply filters
                        if exclude and animal == exclude:
                            continue
                        if filter_func and not filter_func(animal):
                            continue
                        candidates.append(animal)
        
        # Filter by actual distance (cell-based search may include animals slightly outside radius)
        radius_sq = radius * radius
        result = []
        for animal in candidates:
            dx = animal.x - x
            dy = animal.y - y
            dist_sq = dx * dx + dy * dy
            if dist_sq <= radius_sq:
                result.append(animal)
        
        return result
    
    def find_nearest(
        self,
        x: float,
        y: float,
        candidates: List[Animal],
        max_distance: float = float('inf'),
        exclude: Optional[Animal] = None
    ) -> Optional[Animal]:
        """
        Find the nearest animal from a list of candidates.
        
        This is a helper method that uses spatial partitioning to quickly
        filter candidates before doing distance calculations.
        
        Args:
            x: X coordinate to search from
            y: Y coordinate to search from
            candidates: List of candidate animals (can be pre-filtered)
            max_distance: Maximum distance to search
            exclude: Animal to exclude from search
            
        Returns:
            Optional[Animal]: Nearest animal within max_distance, or None
        """
        if not candidates:
            return None
        
        # If max_distance is specified, use spatial grid to filter
        if max_distance < float('inf'):
            nearby = self.get_nearby_animals(x, y, max_distance, exclude=exclude)
            # Filter to only include animals in candidates list
            nearby = [a for a in nearby if a in candidates]
            if not nearby:
                return None
            candidates = nearby
        
        # Find nearest from filtered candidates
        nearest = None
        min_dist_sq = max_distance * max_distance
        
        for animal in candidates:
            if exclude and animal == exclude:
                continue
            if not animal.is_alive():
                continue
            
            dx = animal.x - x
            dy = animal.y - y
            dist_sq = dx * dx + dy * dy
            
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                nearest = animal
        
        return nearest
    
    def clear(self):
        """Clear all animals from the grid."""
        self.grid.clear()
        self._animal_cells.clear()

