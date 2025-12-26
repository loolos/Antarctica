# Performance Optimization - Spatial Partitioning

## Overview

This document describes the spatial partitioning optimization implemented to improve simulation performance.

## Problem

The original implementation used O(n) linear search to find nearest neighbors. With many animals in the simulation, this became a performance bottleneck, especially when:
- Multiple animals are searching for prey simultaneously
- Animals are checking for nearby predators
- Finding breeding partners

## Solution: Grid-Based Spatial Partitioning

We implemented a `SpatialGrid` class that divides the world into a grid of cells. Each animal is stored in the cell corresponding to its position.

### How It Works

1. **Grid Division**: The world is divided into cells (default: 100x100 pixels)
2. **Animal Tracking**: Each animal is stored in the cell(s) corresponding to its position
3. **Efficient Queries**: When searching for neighbors, we only check the current cell and adjacent cells
4. **Automatic Updates**: When animals move, they are automatically moved to the correct cell

### Performance Improvement

- **Before**: O(n) - Check all animals
- **After**: O(k) - Check only animals in nearby cells, where k << n

For a typical simulation with 65 animals (10 penguins, 5 seals, 50 fish):
- **Before**: Up to 65 distance calculations per query
- **After**: ~5-15 distance calculations per query (only animals in 3x3 grid cells)

### Implementation Details

#### SpatialGrid Class

Located in `simulation/spatial.py`, the `SpatialGrid` class provides:

- `add(animal)`: Add animal to grid
- `remove(animal)`: Remove animal from grid
- `update(animal)`: Update animal position (moves to correct cell)
- `get_nearby_animals(x, y, radius)`: Get all animals within radius
- `find_nearest(x, y, candidates, max_distance)`: Find nearest animal from candidates

#### Integration Points

The spatial grid is integrated into `SimulationEngine`:

1. **Initialization**: Grid is created in `__init__`
2. **Animal Creation**: Animals are added to grid when created (initialization, breeding, spawning)
3. **Movement**: Grid is updated after each animal movement
4. **Removal**: Animals are removed from grid when they die or are eaten
5. **Queries**: `_find_nearest()` uses spatial grid when `max_distance` is specified

### Configuration

The grid cell size is configurable (default: 100 pixels). This balances:
- **Precision**: Smaller cells = more precise but more cells to check
- **Performance**: Larger cells = fewer cells but less precise

For the current world size (800x600), 100-pixel cells create an 8x6 grid, which is optimal for most queries.

### Usage Example

```python
# Spatial grid is automatically used in _find_nearest()
# when max_distance is specified

# This uses spatial grid optimization:
nearest_prey = self._find_nearest(animal, valid_prey, max_distance=200)

# This uses linear search (unlimited distance):
nearest_any = self._find_nearest(animal, all_animals, max_distance=float('inf'))
```

### Benefits

1. **Faster Queries**: Significant reduction in distance calculations
2. **Scalability**: Performance improves as more animals are added
3. **Transparent**: No changes needed to existing code using `_find_nearest()`
4. **Automatic**: Grid updates happen automatically during normal simulation flow

### Future Optimizations

Potential further optimizations:
1. **Dynamic Cell Size**: Adjust cell size based on animal density
2. **Quadtree**: For more complex spatial queries
3. **Caching**: Cache recent queries for frequently accessed positions
4. **Parallel Processing**: Process multiple grid cells in parallel

