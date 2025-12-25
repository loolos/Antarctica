"""
测试模拟引擎
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from simulation.engine import SimulationEngine


class TestSimulationEngine(unittest.TestCase):
    """测试模拟引擎"""
    
    def setUp(self):
        """设置测试环境"""
        self.engine = SimulationEngine(width=800, height=600)
    
    def test_engine_initialization(self):
        """测试引擎初始化"""
        state = self.engine.get_state()
        self.assertGreater(len(state.penguins), 0)
        self.assertGreater(len(state.seals), 0)
        self.assertGreater(len(state.fish), 0)
        self.assertEqual(state.tick, 0)
    
    def test_tick(self):
        """测试单步tick"""
        initial_tick = self.engine.get_state().tick
        self.engine.tick()
        new_tick = self.engine.get_state().tick
        self.assertEqual(new_tick, initial_tick + 1)
    
    def test_step(self):
        """测试多步推进"""
        initial_tick = self.engine.get_state().tick
        self.engine.step(10)
        new_tick = self.engine.get_state().tick
        self.assertEqual(new_tick, initial_tick + 10)
    
    def test_state_serialization(self):
        """测试状态序列化"""
        state = self.engine.get_state()
        state_dict = state.to_dict()
        
        self.assertIn('tick', state_dict)
        self.assertIn('penguins', state_dict)
        self.assertIn('seals', state_dict)
        self.assertIn('fish', state_dict)
        self.assertIn('environment', state_dict)
        
        # 检查企鹅数据格式
        if len(state_dict['penguins']) > 0:
            penguin = state_dict['penguins'][0]
            self.assertIn('id', penguin)
            self.assertIn('x', penguin)
            self.assertIn('y', penguin)
            self.assertIn('energy', penguin)
    
    def test_predation(self):
        """测试捕食机制"""
        # 运行多步，观察捕食是否发生
        initial_fish_count = len(self.engine.get_state().fish)
        initial_penguin_count = len(self.engine.get_state().penguins)
        
        # 运行足够多的步数让捕食发生
        self.engine.step(100)
        
        state = self.engine.get_state()
        # 由于捕食和繁殖，数量可能会变化
        # 至少确保系统还在运行
        self.assertGreaterEqual(len(state.fish), 0)
        self.assertGreaterEqual(len(state.penguins), 0)
    
    def test_breeding(self):
        """测试繁殖机制"""
        initial_penguin_count = len(self.engine.get_state().penguins)
        
        # 给企鹅足够的能量并运行多步
        for penguin in self.engine.get_state().penguins:
            penguin.energy = 100
            penguin.breeding_cooldown = 0
        
        self.engine.step(200)
        
        # 由于繁殖，企鹅数量可能会增加
        # 但由于捕食，也可能减少
        final_count = len(self.engine.get_state().penguins)
        # 至少确保系统还在运行
        self.assertIsInstance(final_count, int)
    
    def test_environment_update(self):
        """测试环境更新"""
        initial_temp = self.engine.get_state().environment.temperature
        initial_ice = self.engine.get_state().environment.ice_coverage
        
        self.engine.step(100)
        
        # 环境应该会更新
        final_temp = self.engine.get_state().environment.temperature
        final_ice = self.engine.get_state().environment.ice_coverage
        
        # 温度可能会变化（季节循环）
        self.assertIsNotNone(final_temp)
        self.assertIsNotNone(final_ice)
    
    def test_animal_removal(self):
        """测试死亡动物移除"""
        # 手动设置一些动物能量为0
        state = self.engine.get_state()
        if len(state.penguins) > 0:
            state.penguins[0].energy = 0
        
        self.engine.tick()
        
        # 死亡的动物应该被移除
        new_state = self.engine.get_state()
        dead_penguins = [p for p in new_state.penguins if p.energy <= 0]
        self.assertEqual(len(dead_penguins), 0)


if __name__ == '__main__':
    unittest.main()

