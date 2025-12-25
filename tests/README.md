# 测试系统文档

## 测试结构

```
tests/
├── test_animals.py      # 动物类单元测试
├── test_environment.py  # 环境类单元测试
├── test_engine.py       # 模拟引擎测试
├── test_integration.py  # 集成测试
└── run_tests.py        # 测试运行器
```

## 运行测试

### 方法1: 使用测试运行器
```bash
python tests/run_tests.py
```

### 方法2: 使用unittest
```bash
python -m unittest discover tests
```

### 方法3: 运行单个测试文件
```bash
python -m unittest tests.test_animals
python -m unittest tests.test_environment
python -m unittest tests.test_engine
python -m unittest tests.test_integration
```

## 测试覆盖

### 1. 动物类测试 (test_animals.py)
- ✅ 企鹅创建和基本属性
- ✅ 动物移动和边界检查
- ✅ 能量消耗和恢复
- ✅ 繁殖机制
- ✅ 死亡判定
- ✅ 距离计算

### 2. 环境类测试 (test_environment.py)
- ✅ 环境初始化
- ✅ 陆地/海洋检测
- ✅ 冰厚度计算
- ✅ 环境更新（季节变化）

### 3. 模拟引擎测试 (test_engine.py)
- ✅ 引擎初始化
- ✅ Tick和Step功能
- ✅ 状态序列化
- ✅ 捕食机制
- ✅ 繁殖机制
- ✅ 环境更新
- ✅ 死亡动物移除

### 4. 集成测试 (test_integration.py)
- ✅ 完整模拟周期
- ✅ 状态一致性
- ✅ JSON序列化
- ✅ 长时间运行稳定性

## 测试结果示例

运行测试后，你应该看到类似以下的输出：

```
test_animal_creation ... ok
test_animal_move ... ok
test_engine_initialization ... ok
test_tick ... ok
...

----------------------------------------------------------------------
Ran 25 tests in 0.123s

OK
```

## 添加新测试

1. 在对应的测试文件中添加新的测试方法
2. 测试方法名必须以`test_`开头
3. 使用`self.assert*`方法进行断言
4. 运行测试验证新功能

示例：
```python
def test_new_feature(self):
    """测试新功能"""
    # 准备
    engine = SimulationEngine()
    
    # 执行
    engine.step(10)
    
    # 验证
    state = engine.get_state()
    self.assertEqual(state.tick, 10)
```

