# Testing System Documentation

## Test Types

### 1. Quick Test (`test_quick.py`)
Simple functionality verification test, suitable for quickly checking if the system works correctly.

**Run Method**:
```bash
python test_quick.py
```

**Test Content**:
- Module imports
- Engine basic functionality
- Animal classes
- Environment class
- State serialization
- Simulation run

### 2. Unit Tests (`tests/test_*.py`)
Complete test suite using Python unittest framework.

**Run Method**:
```bash
# Run all tests
python tests/run_tests.py

# Or use unittest
python -m unittest discover tests

# Run specific test file
python -m unittest tests.test_animals
python -m unittest tests.test_environment
python -m unittest tests.test_engine
python -m unittest tests.test_integration
```

### 3. Integration Test (`test_simulation.py`)
Simple end-to-end test, verifies the entire simulation flow.

**Run Method**:
```bash
python test_simulation.py
```

## Test Coverage Details

### test_animals.py - Animal Class Tests
- ✅ Penguin creation and attributes
- ✅ Seal creation and attributes
- ✅ Fish creation and attributes
- ✅ Animal movement and boundary checks
- ✅ Energy consumption and recovery
- ✅ Breeding mechanism
- ✅ Death determination
- ✅ Distance calculation

### test_environment.py - Environment Class Tests
- ✅ Environment initialization
- ✅ Land/sea detection
- ✅ Ice thickness calculation
- ✅ Environment update (seasonal changes)

### test_engine.py - Simulation Engine Tests
- ✅ Engine initialization
- ✅ Tick functionality
- ✅ Step functionality
- ✅ State serialization
- ✅ Predation mechanism
- ✅ Breeding mechanism
- ✅ Environment update
- ✅ Dead animal removal

### test_integration.py - Integration Tests
- ✅ Complete simulation cycle (1000 steps)
- ✅ State consistency verification
- ✅ JSON serialization/deserialization
- ✅ Long-running stability (5000 steps)

## Test Result Interpretation

### Success Output Example
```
test_animal_creation ... ok
test_animal_move ... ok
test_engine_initialization ... ok
...

----------------------------------------------------------------------
Ran 25 tests in 0.123s

OK
```

### Failure Output Example
```
test_something ... FAIL

======================================================================
FAIL: test_something (tests.test_engine.TestSimulationEngine)
----------------------------------------------------------------------
Traceback (most recent call last):
  ...
AssertionError: ...

----------------------------------------------------------------------
Ran 25 tests in 0.123s

FAILED (failures=1)
```

## Writing New Tests

### Basic Structure
```python
import unittest
from simulation.engine import SimulationEngine

class TestNewFeature(unittest.TestCase):
    def test_feature_name(self):
        """Test description"""
        # Arrange
        engine = SimulationEngine()
        
        # Act
        engine.step(10)
        
        # Assert
        state = engine.get_state()
        self.assertEqual(state.tick, 10)
```

### Common Assertion Methods
- `self.assertEqual(a, b)` - Equal
- `self.assertNotEqual(a, b)` - Not equal
- `self.assertTrue(x)` - True
- `self.assertFalse(x)` - False
- `self.assertIsNone(x)` - Is None
- `self.assertIsNotNone(x)` - Is not None
- `self.assertIn(item, list)` - Contains
- `self.assertGreater(a, b)` - Greater than
- `self.assertLess(a, b)` - Less than
- `self.assertAlmostEqual(a, b, places=2)` - Approximately equal

## Continuous Integration Suggestions

You can add tests to CI/CD workflows:

```yaml
# .github/workflows/test.yml example
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: python tests/run_tests.py
```

## Performance Testing

For performance testing, you can run long simulations:

```python
import time
from simulation.engine import SimulationEngine

engine = SimulationEngine()
start = time.time()
engine.step(10000)
end = time.time()
print(f"10000 steps in {end - start:.2f} seconds")
```

## Debugging Tests

If tests fail, you can:

1. Run with verbose output:
```bash
python -m unittest tests.test_engine -v
```

2. Add print statements in tests:
```python
def test_something(self):
    state = engine.get_state()
    print(f"Debug: penguins={len(state.penguins)}")
    # ...
```

3. Use debugger:
```bash
python -m pdb tests/run_tests.py
```
