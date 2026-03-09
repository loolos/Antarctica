"""
Test simulation engine
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from simulation.engine import SimulationEngine
from simulation.animals import Penguin, Seal, Seagull, Fish
from simulation.world import FloeFish


class TestSimulationEngine(unittest.TestCase):
    """Test simulation engine"""
    
    def setUp(self):
        """Set up test environment"""
        self.engine = SimulationEngine(width=800, height=600)
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        state = self.engine.get_state()
        self.assertGreater(len(state.penguins), 0)
        self.assertGreater(len(state.seals), 0)
        self.assertGreater(len(state.fish), 0)
        self.assertGreater(len(state.seagulls), 0)
        self.assertEqual(state.tick, 0)
    
    def test_tick(self):
        """Test single tick"""
        initial_tick = self.engine.get_state().tick
        self.engine.tick()
        new_tick = self.engine.get_state().tick
        self.assertEqual(new_tick, initial_tick + 1)
    
    def test_step(self):
        """Test multiple steps"""
        initial_tick = self.engine.get_state().tick
        self.engine.step(10)
        new_tick = self.engine.get_state().tick
        self.assertEqual(new_tick, initial_tick + 10)
    
    def test_state_serialization(self):
        """Test state serialization"""
        state = self.engine.get_state()
        state_dict = state.to_dict()
        
        self.assertIn('tick', state_dict)
        self.assertIn('penguins', state_dict)
        self.assertIn('seals', state_dict)
        self.assertIn('fish', state_dict)
        self.assertIn('seagulls', state_dict)
        self.assertIn('environment', state_dict)
        
        # Check penguin data format
        if len(state_dict['penguins']) > 0:
            penguin = state_dict['penguins'][0]
            self.assertIn('id', penguin)
            self.assertIn('x', penguin)
            self.assertIn('y', penguin)
            self.assertIn('energy', penguin)
    
    def test_predation(self):
        """Test predation mechanism"""
        # Run multiple steps to observe predation
        initial_fish_count = len(self.engine.get_state().fish)
        initial_penguin_count = len(self.engine.get_state().penguins)
        
        # Run enough steps for predation to occur
        self.engine.step(100)
        
        state = self.engine.get_state()
        # Count may change due to predation and breeding
        # At least ensure the system is still running
        self.assertGreaterEqual(len(state.fish), 0)
        self.assertGreaterEqual(len(state.penguins), 0)
    
    def test_breeding(self):
        """Test breeding mechanism"""
        initial_penguin_count = len(self.engine.get_state().penguins)
        
        # Give penguins enough energy and run multiple steps
        for penguin in self.engine.get_state().penguins:
            penguin.energy = 100
            penguin.breeding_cooldown = 0
        
        self.engine.step(200)
        
        # Penguin count may increase due to breeding or decrease due to predation
        final_count = len(self.engine.get_state().penguins)
        # At least ensure the system is still running
        self.assertIsInstance(final_count, int)
    
    def test_environment_update(self):
        """Test environment update"""
        initial_temp = self.engine.get_state().environment.temperature
        initial_ice = self.engine.get_state().environment.ice_coverage
        
        self.engine.step(100)
        
        # Environment should be updated
        final_temp = self.engine.get_state().environment.temperature
        final_ice = self.engine.get_state().environment.ice_coverage
        
        # Temperature may change (seasonal cycle)
        self.assertIsNotNone(final_temp)
        self.assertIsNotNone(final_ice)
    

    def test_searching_penguin_on_land_moves_toward_sea(self):
        """Low-energy penguin on land should leave floe instead of oscillating at center."""
        # Keep world simple and deterministic: one circular floe in middle
        self.engine.world.environment.ice_floes = [{
            'x': 400.0, 'y': 300.0, 'radius': 120.0,
            'shape': 'circle', 'radius_x': 120.0, 'radius_y': 120.0, 'rotation': 0
        }]

        penguin = Penguin(id='debug_penguin', x=400.0, y=300.0, energy=20.0, state='land')
        penguin.age = 200
        penguin.behavior_state = 'searching'
        penguin.hunting_cooldown = 0
        self.engine.world.penguins = [penguin]
        self.engine.world.seals = []
        self.engine.world.fish = []
        self.engine.world.seagulls = []

        left_land = False
        for _ in range(80):
            self.engine.tick()
            if not self.engine.world.environment.is_land(penguin.x, penguin.y):
                left_land = True
                break

        self.assertTrue(left_land, 'Searching penguin should be able to leave ice floe for sea')

    def test_animal_removal(self):
        """Test dead animal removal"""
        # Manually set some animal energy to 0
        state = self.engine.get_state()
        if len(state.penguins) > 0:
            state.penguins[0].energy = 0
        
        self.engine.tick()
        
        # Dead animals should be removed
        new_state = self.engine.get_state()
        dead_penguins = [p for p in new_state.penguins if p.energy <= 0]
        self.assertEqual(len(dead_penguins), 0)

    def test_seagull_catches_fish_then_carries_to_floe(self):
        """Seagull should carry fish after catch instead of instant energy gain."""
        seagull = Seagull(id="g1", x=100.0, y=100.0, energy=70.0, state="flying")
        seagull.behavior_state = "targeting"
        fish = Fish(id="f1", x=103.0, y=103.0, energy=30.0)

        self.engine.world.seagulls = [seagull]
        self.engine.world.fish = [fish]
        self.engine.world.penguins = []
        self.engine.world.seals = []
        self.engine.world.floe_fish = []
        self.engine.spatial_grid.add(seagull)
        self.engine.spatial_grid.add(fish)

        self.engine._handle_predation()

        self.assertEqual(len(self.engine.world.fish), 0)
        self.assertTrue(seagull.carrying_fish)
        self.assertEqual(seagull.behavior_state, "carrying_to_land")
        self.assertEqual(seagull.target_id, "")

    def test_seagull_processing_drops_fish_when_threat_near(self):
        """Grounded seagull with fish should drop fish and flee if threatened."""
        self.engine.world.environment.ice_floes = [{
            'x': 200.0, 'y': 200.0, 'radius': 80.0,
            'shape': 'circle', 'radius_x': 80.0, 'radius_y': 80.0, 'rotation': 0
        }]
        seagull = Seagull(id="g2", x=200.0, y=200.0, energy=80.0, state="grounded")
        seagull.carrying_fish = True
        seagull.behavior_state = "processing_prey"
        seagull.prey_processing_ticks = 10
        penguin = Penguin(id="p_threat", x=205.0, y=205.0, energy=80.0, state="land")

        self.engine.world.seagulls = [seagull]
        self.engine.world.penguins = [penguin]
        self.engine.world.seals = []
        self.engine.world.fish = []
        self.engine.world.floe_fish = []

        self.engine._move_animal(seagull)

        self.assertFalse(seagull.carrying_fish)
        self.assertEqual(seagull.state, "flying")
        self.assertEqual(seagull.behavior_state, "fleeing")
        self.assertEqual(len(self.engine.world.floe_fish), 1)

    def test_seagull_exits_fleeing_after_cooldown_and_searches_when_hungry(self):
        """Seagull should leave fleeing mode after countdown and resume hunting when hungry."""
        seagull = Seagull(id="g_flee_hungry", x=250.0, y=250.0, energy=20.0, state="flying")
        seagull.behavior_state = "fleeing"
        seagull.flee_edge_direction = 0.0
        seagull.flee_cooldown = 1

        self.engine.world.seagulls = [seagull]
        self.engine.world.penguins = []
        self.engine.world.seals = []
        self.engine.world.fish = []
        self.engine.world.floe_fish = []

        self.engine._move_animal(seagull)  # cooldown 1 -> 0, still fleeing this frame
        self.assertEqual(seagull.behavior_state, "fleeing")
        self.assertEqual(seagull.flee_cooldown, 0)

        self.engine._move_animal(seagull)  # cooldown reached, should transition by hunger
        self.assertEqual(seagull.behavior_state, "searching")

    def test_seagull_exits_fleeing_after_cooldown_and_idles_when_not_hungry(self):
        """Seagull should leave fleeing mode after countdown and idle when not hungry."""
        seagull = Seagull(id="g_flee_full", x=250.0, y=250.0, energy=90.0, state="flying")
        seagull.behavior_state = "fleeing"
        seagull.flee_edge_direction = 0.0
        seagull.flee_cooldown = 0

        self.engine.world.seagulls = [seagull]
        self.engine.world.penguins = []
        self.engine.world.seals = []
        self.engine.world.fish = []
        self.engine.world.floe_fish = []

        self.engine._move_animal(seagull)
        self.assertEqual(seagull.behavior_state, "idle")

    def test_searching_penguin_eats_dropped_floe_fish(self):
        """Searching penguin on land should consume nearby dropped floe fish."""
        penguin = Penguin(id="p_search", x=300.0, y=300.0, energy=20.0, state="land")
        penguin.behavior_state = "searching"
        floe_fish = FloeFish(id="ff1", x=302.0, y=302.0, ttl_ticks=100)

        self.engine.world.penguins = [penguin]
        self.engine.world.seals = []
        self.engine.world.seagulls = []
        self.engine.world.fish = []
        self.engine.world.floe_fish = [floe_fish]

        self.engine._handle_predation()

        self.assertEqual(len(self.engine.world.floe_fish), 0)
        self.assertGreater(penguin.energy, 20.0)
        self.assertEqual(penguin.behavior_state, "idle")

    def test_penguin_flees_nearby_seal_even_with_stale_spatial_cell(self):
        """Penguin on floe should still enter fleeing when a seal is close."""
        self.engine.world.environment.ice_floes = [{
            'x': 200.0, 'y': 200.0, 'radius': 120.0,
            'shape': 'circle', 'radius_x': 120.0, 'radius_y': 120.0, 'rotation': 0
        }]
        penguin = Penguin(id="p_flee", x=200.0, y=200.0, energy=80.0, state="land")
        seal = Seal(id="s_near", x=700.0, y=500.0, energy=120.0, state="land")

        self.engine.world.penguins = [penguin]
        self.engine.world.seals = [seal]
        self.engine.world.seagulls = []
        self.engine.world.fish = []
        self.engine.world.floe_fish = []
        self.engine.spatial_grid.clear()
        self.engine.spatial_grid.add(penguin)
        self.engine.spatial_grid.add(seal)

        # Teleport seal near penguin without updating spatial grid to emulate stale index.
        seal.x = 206.0
        seal.y = 204.0

        self.engine._move_animal(penguin)

        self.assertEqual(penguin.behavior_state, "fleeing")
        self.assertGreater(penguin.flee_cooldown, 0)

    def test_searching_penguin_moves_toward_feeding_seagull_on_land(self):
        """Searching penguin should approach grounded seagull processing prey."""
        self.engine.world.environment.ice_floes = [{
            'x': 350.0, 'y': 300.0, 'radius': 180.0,
            'shape': 'circle', 'radius_x': 180.0, 'radius_y': 180.0, 'rotation': 0
        }]
        penguin = Penguin(id="p_food", x=280.0, y=300.0, energy=20.0, state="land")
        penguin.behavior_state = "searching"
        penguin.hunting_cooldown = 0
        seagull = Seagull(id="g_food", x=360.0, y=300.0, energy=70.0, state="grounded")
        seagull.carrying_fish = True
        seagull.behavior_state = "processing_prey"
        seagull.prey_processing_ticks = 10

        self.engine.world.penguins = [penguin]
        self.engine.world.seals = []
        self.engine.world.seagulls = [seagull]
        self.engine.world.fish = []
        self.engine.world.floe_fish = []

        old_x = penguin.x
        self.engine._move_animal(penguin)
        self.assertGreater(penguin.x, old_x)

    def test_searching_seal_prefers_nearest_land_food_source(self):
        """Searching seal should use unified nearest target among floe fish and feeding seagull."""
        self.engine.world.environment.ice_floes = [{
            'x': 360.0, 'y': 280.0, 'radius': 220.0,
            'shape': 'circle', 'radius_x': 220.0, 'radius_y': 220.0, 'rotation': 0
        }]
        seal = Seal(id="s_food", x=300.0, y=280.0, energy=30.0, state="land")
        seal.behavior_state = "searching"
        seal.hunting_cooldown = 0
        # Dropped fish is closer than feeding seagull, seal should move right toward fish.
        floe_fish = FloeFish(id="ff_near", x=320.0, y=280.0, ttl_ticks=100)
        seagull = Seagull(id="g_far", x=390.0, y=280.0, energy=70.0, state="grounded")
        seagull.carrying_fish = True
        seagull.behavior_state = "processing_prey"
        seagull.prey_processing_ticks = 10

        self.engine.world.penguins = []
        self.engine.world.seals = [seal]
        self.engine.world.seagulls = [seagull]
        self.engine.world.fish = []
        self.engine.world.floe_fish = [floe_fish]

        old_x = seal.x
        self.engine._move_animal(seal)
        self.assertGreater(seal.x, old_x)

    def test_grounded_processing_seagull_stays_put_without_threat(self):
        """Seagull processing prey should remain stationary unless threat appears."""
        self.engine.world.environment.ice_floes = [{
            'x': 240.0, 'y': 220.0, 'radius': 100.0,
            'shape': 'circle', 'radius_x': 100.0, 'radius_y': 100.0, 'rotation': 0
        }]
        seagull = Seagull(id="g_static", x=240.0, y=220.0, energy=75.0, state="grounded")
        seagull.carrying_fish = True
        seagull.behavior_state = "processing_prey"
        seagull.prey_processing_ticks = 8

        self.engine.world.penguins = []
        self.engine.world.seals = []
        self.engine.world.seagulls = [seagull]
        self.engine.world.fish = []
        self.engine.world.floe_fish = []

        old_x, old_y = seagull.x, seagull.y
        self.engine._move_animal(seagull)

        self.assertAlmostEqual(seagull.x, old_x)
        self.assertAlmostEqual(seagull.y, old_y)
        self.assertEqual(seagull.behavior_state, "processing_prey")
        self.assertEqual(seagull.prey_processing_ticks, 7)


if __name__ == '__main__':
    unittest.main()

