"""
Test animal classes
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from simulation.animals import Penguin, Seal, Fish


class TestAnimals(unittest.TestCase):
    """Test animal classes"""
    
    def test_penguin_creation(self):
        """Test penguin creation"""
        penguin = Penguin(id="test_penguin", x=100, y=200, energy=80)
        self.assertEqual(penguin.id, "test_penguin")
        self.assertEqual(penguin.x, 100)
        self.assertEqual(penguin.y, 200)
        self.assertEqual(penguin.energy, 80)
        self.assertEqual(penguin.state, "land")
    
    def test_penguin_move(self):
        """Test penguin movement"""
        penguin = Penguin(id="test", x=100, y=100, energy=80)
        penguin.move(10, 20, 800, 600)
        self.assertEqual(penguin.x, 110)
        self.assertEqual(penguin.y, 120)
        self.assertLess(penguin.energy, 80)  # Movement consumes energy
    
    def test_penguin_energy_consumption(self):
        """Test penguin energy consumption"""
        penguin = Penguin(id="test", x=100, y=100, energy=50)
        initial_energy = penguin.energy
        penguin.tick()
        self.assertLess(penguin.energy, initial_energy)
    
    def test_penguin_breeding(self):
        """Test penguin breeding"""
        penguin = Penguin(id="test", x=100, y=100, energy=100)
        self.assertTrue(penguin.can_breed())
        baby = penguin.breed()
        self.assertIsInstance(baby, Penguin)
        self.assertNotEqual(baby.id, penguin.id)
        self.assertFalse(penguin.can_breed())  # Cooldown after breeding
    
    def test_seal_creation(self):
        """Test seal creation"""
        seal = Seal(id="test_seal", x=200, y=300, energy=120)
        self.assertEqual(seal.id, "test_seal")
        self.assertEqual(seal.state, "sea")
    
    def test_seal_predation(self):
        """Test seal energy gain"""
        seal = Seal(id="test", x=100, y=100, energy=50)
        initial_energy = seal.energy
        seal.gain_energy(30)
        self.assertEqual(seal.energy, initial_energy + 30)
        self.assertLessEqual(seal.energy, seal.max_energy)
    
    def test_fish_creation(self):
        """Test fish creation"""
        fish = Fish(id="test_fish", x=150, y=250, energy=30)
        self.assertEqual(fish.id, "test_fish")
        self.assertGreater(fish.speed, 0)
    
    def test_animal_death(self):
        """Test animal death"""
        penguin = Penguin(id="test", x=100, y=100, energy=0)
        self.assertFalse(penguin.is_alive())
        
        penguin2 = Penguin(id="test2", x=100, y=100, energy=50, age=2000)
        self.assertFalse(penguin2.is_alive())  # Exceeds max age
    
    def test_animal_age_boundary(self):
        """Test animal age boundary"""
        penguin = Penguin(id="edge", x=100, y=100, energy=50)
        penguin.age = penguin.max_age - 1
        self.assertTrue(penguin.is_alive())

        penguin.age = penguin.max_age
        self.assertFalse(penguin.is_alive())

    def test_animal_distance(self):
        """Test animal distance calculation"""
        p1 = Penguin(id="p1", x=0, y=0, energy=50)
        p2 = Penguin(id="p2", x=3, y=4, energy=50)
        distance = p1.distance_to(p2)
        self.assertAlmostEqual(distance, 5.0, places=1)


if __name__ == '__main__':
    unittest.main()

