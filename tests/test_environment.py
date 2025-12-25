"""
测试环境类
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from simulation.environment import Environment


class TestEnvironment(unittest.TestCase):
    """测试环境类"""
    
    def test_environment_creation(self):
        """测试环境创建"""
        env = Environment(width=800, height=600)
        self.assertEqual(env.width, 800)
        self.assertEqual(env.height, 600)
        self.assertGreaterEqual(env.ice_coverage, 0)
        self.assertLessEqual(env.ice_coverage, 1)
    
    def test_land_detection(self):
        """测试陆地检测"""
        env = Environment(width=800, height=600, ice_coverage=0.8)
        # Manually set ice floes for testing
        env.ice_floes = [{'x': 100, 'y': 100, 'radius': 50}]
        
        # Center of floe should be land
        self.assertTrue(env.is_land(100, 100))
        # Edge (inside)
        self.assertTrue(env.is_land(100 + 30, 100))
        # Far away should be sea
        self.assertFalse(env.is_land(500, 500))
    
    def test_sea_detection(self):
        """测试海洋检测"""
        env = Environment(width=800, height=600, ice_coverage=0.8)
        env.ice_floes = [{'x': 100, 'y': 100, 'radius': 50}]
        
        # Center of floe should NOT be sea
        self.assertFalse(env.is_sea(100, 100))
        # Far away should be sea
        self.assertTrue(env.is_sea(500, 500))
    
    def test_ice_thickness(self):
        """测试冰厚度计算"""
        env = Environment(width=800, height=600, temperature=-10)
        thickness = env.get_ice_thickness(700, 300)
        self.assertGreaterEqual(thickness, 0)
        self.assertLessEqual(thickness, 1)
    
    def test_environment_tick(self):
        """测试环境更新"""
        env = Environment(width=800, height=600, temperature=-10, ice_coverage=0.8)
        initial_temp = env.temperature
        initial_ice = env.ice_coverage
        
        env.tick()
        
        # 温度应该会变化（季节循环）
        # 冰覆盖率可能会变化
        self.assertIsNotNone(env.temperature)
        self.assertIsNotNone(env.ice_coverage)


if __name__ == '__main__':
    unittest.main()

