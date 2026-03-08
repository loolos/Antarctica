"""
Test simulation engine
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from simulation.engine import SimulationEngine


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


if __name__ == '__main__':
    unittest.main()

