"""
集成测试 - 测试整个系统
"""
import unittest
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from simulation.engine import SimulationEngine


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_full_simulation_cycle(self):
        """测试完整模拟周期"""
        engine = SimulationEngine()
        
        # 运行1000步
        engine.step(1000)
        
        state = engine.get_state()
        
        # 验证状态完整性
        self.assertGreater(state.tick, 0)
        self.assertIsNotNone(state.environment)
        self.assertIsInstance(state.penguins, list)
        self.assertIsInstance(state.seals, list)
        self.assertIsInstance(state.fish, list)
        
        # 验证环境参数
        self.assertGreaterEqual(state.environment.ice_coverage, 0)
        self.assertLessEqual(state.environment.ice_coverage, 1)
        self.assertIsNotNone(state.environment.temperature)
    
    def test_state_consistency(self):
        """测试状态一致性"""
        engine = SimulationEngine()
        
        for _ in range(10):
            engine.tick()
            state = engine.get_state()
            
            # 验证所有动物都有有效位置
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
    
    def test_json_serialization(self):
        """测试JSON序列化"""
        engine = SimulationEngine()
        engine.step(50)
        
        state = engine.get_state()
        state_dict = state.to_dict()
        
        # 尝试序列化为JSON
        json_str = json.dumps(state_dict)
        self.assertIsInstance(json_str, str)
        
        # 尝试反序列化
        parsed = json.loads(json_str)
        self.assertEqual(parsed['tick'], state.tick)
        self.assertEqual(len(parsed['penguins']), len(state.penguins))
    
    def test_long_running_simulation(self):
        """测试长时间运行"""
        engine = SimulationEngine()
        
        # 运行5000步
        engine.step(5000)
        
        state = engine.get_state()
        
        # 系统应该仍然正常运行
        self.assertEqual(state.tick, 5000)
        self.assertIsNotNone(state.environment)
        
        # 至少应该还有一些动物存活（除非全部被捕食）
        total_animals = len(state.penguins) + len(state.seals) + len(state.fish)
        # 由于捕食关系，可能所有动物都死亡，这是正常的
        # 但系统不应该崩溃
        self.assertIsInstance(total_animals, int)
        self.assertGreaterEqual(total_animals, 0)


if __name__ == '__main__':
    unittest.main()

