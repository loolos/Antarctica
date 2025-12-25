"""
测试动物类
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from simulation.animals import Penguin, Seal, Fish


class TestAnimals(unittest.TestCase):
    """测试动物类"""
    
    def test_penguin_creation(self):
        """测试企鹅创建"""
        penguin = Penguin(id="test_penguin", x=100, y=200, energy=80)
        self.assertEqual(penguin.id, "test_penguin")
        self.assertEqual(penguin.x, 100)
        self.assertEqual(penguin.y, 200)
        self.assertEqual(penguin.energy, 80)
        self.assertEqual(penguin.state, "land")
    
    def test_penguin_move(self):
        """测试企鹅移动"""
        penguin = Penguin(id="test", x=100, y=100, energy=80)
        penguin.move(10, 20, 800, 600)
        self.assertEqual(penguin.x, 110)
        self.assertEqual(penguin.y, 120)
        self.assertLess(penguin.energy, 80)  # 移动消耗能量
    
    def test_penguin_energy_consumption(self):
        """测试企鹅能量消耗"""
        penguin = Penguin(id="test", x=100, y=100, energy=50)
        initial_energy = penguin.energy
        penguin.tick()
        self.assertLess(penguin.energy, initial_energy)
    
    def test_penguin_breeding(self):
        """测试企鹅繁殖"""
        penguin = Penguin(id="test", x=100, y=100, energy=100)
        self.assertTrue(penguin.can_breed())
        baby = penguin.breed()
        self.assertIsInstance(baby, Penguin)
        self.assertNotEqual(baby.id, penguin.id)
        self.assertFalse(penguin.can_breed())  # 繁殖后有冷却
    
    def test_seal_creation(self):
        """测试海豹创建"""
        seal = Seal(id="test_seal", x=200, y=300, energy=120)
        self.assertEqual(seal.id, "test_seal")
        self.assertEqual(seal.state, "sea")
    
    def test_seal_predation(self):
        """测试海豹能量获取"""
        seal = Seal(id="test", x=100, y=100, energy=50)
        initial_energy = seal.energy
        seal.gain_energy(30)
        self.assertEqual(seal.energy, initial_energy + 30)
        self.assertLessEqual(seal.energy, seal.max_energy)
    
    def test_fish_creation(self):
        """测试鱼创建"""
        fish = Fish(id="test_fish", x=150, y=250, energy=30)
        self.assertEqual(fish.id, "test_fish")
        self.assertGreater(fish.speed, 0)
    
    def test_animal_death(self):
        """测试动物死亡"""
        penguin = Penguin(id="test", x=100, y=100, energy=0)
        self.assertFalse(penguin.is_alive())
        
        penguin2 = Penguin(id="test2", x=100, y=100, energy=50, age=2000)
        self.assertFalse(penguin2.is_alive())  # 超过最大年龄
    
    def test_animal_distance(self):
        """测试动物距离计算"""
        p1 = Penguin(id="p1", x=0, y=0, energy=50)
        p2 = Penguin(id="p2", x=3, y=4, energy=50)
        distance = p1.distance_to(p2)
        self.assertAlmostEqual(distance, 5.0, places=1)


if __name__ == '__main__':
    unittest.main()

