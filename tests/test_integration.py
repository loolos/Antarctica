"""
Integration tests - test the entire system
"""
import unittest
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from simulation.engine import SimulationEngine


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_full_simulation_cycle(self):
        """Test full simulation cycle"""
        engine = SimulationEngine()
        
        # Run 1000 steps
        engine.step(1000)
        
        state = engine.get_state()
        
        # Verify state integrity
        self.assertGreater(state.tick, 0)
        self.assertIsNotNone(state.environment)
        self.assertIsInstance(state.penguins, list)
        self.assertIsInstance(state.seals, list)
        self.assertIsInstance(state.fish, list)
        self.assertIsInstance(state.seagulls, list)
        
        # Verify environment parameters
        self.assertGreaterEqual(state.environment.ice_coverage, 0)
        self.assertLessEqual(state.environment.ice_coverage, 1)
        self.assertIsNotNone(state.environment.temperature)
    
    def test_state_consistency(self):
        """Test state consistency"""
        engine = SimulationEngine()
        
        for _ in range(10):
            engine.tick()
            state = engine.get_state()
            
            # Verify all animals have valid positions
            for penguin in state.penguins:
                self.assertGreaterEqual(penguin.x, 0)
                self.assertLessEqual(penguin.x, state.environment.width)
                self.assertGreaterEqual(penguin.y, 0)
                self.assertLessEqual(penguin.y, state.environment.height)
                self.assertGreaterEqual(penguin.energy, 0)
            
            for seal in state.seals:
                self.assertGreaterEqual(seal.x, 0)
                self.assertLessEqual(seal.x, state.environment.width)
                self.assertGreaterEqual(seal.y, 0)
                self.assertLessEqual(seal.y, state.environment.height)
            
            for fish in state.fish:
                self.assertGreaterEqual(fish.x, 0)
                self.assertLessEqual(fish.x, state.environment.width)
                self.assertGreaterEqual(fish.y, 0)
                self.assertLessEqual(fish.y, state.environment.height)

            for seagull in state.seagulls:
                self.assertGreaterEqual(seagull.x, 0)
                self.assertLessEqual(seagull.x, state.environment.width)
                self.assertGreaterEqual(seagull.y, 0)
                self.assertLessEqual(seagull.y, state.environment.height)
    
    def test_json_serialization(self):
        """Test JSON serialization"""
        engine = SimulationEngine()
        engine.step(50)
        
        state = engine.get_state()
        state_dict = state.to_dict()
        
        # Try serializing to JSON
        json_str = json.dumps(state_dict)
        self.assertIsInstance(json_str, str)
        
        # Try deserializing
        parsed = json.loads(json_str)
        self.assertEqual(parsed['tick'], state.tick)
        self.assertEqual(len(parsed['penguins']), len(state.penguins))
    
    def test_long_running_simulation(self):
        """Test long-running simulation"""
        engine = SimulationEngine()
        
        # Run 5000 steps
        engine.step(5000)
        
        state = engine.get_state()
        
        # System should still be running normally
        self.assertEqual(state.tick, 5000)
        self.assertIsNotNone(state.environment)
        
        # At least some animals may survive (unless all are predated)
        total_animals = len(state.penguins) + len(state.seals) + len(state.fish) + len(state.seagulls)
        # Due to predation, all animals may die, which is normal
        # But the system should not crash
        self.assertIsInstance(total_animals, int)
        self.assertGreaterEqual(total_animals, 0)


if __name__ == '__main__':
    unittest.main()

