# Testing System Documentation

## Test Structure

```
tests/
├── test_animals.py      # Animal class unit tests
├── test_environment.py  # Environment class unit tests
├── test_engine.py       # Simulation engine tests
├── test_integration.py  # Integration tests
└── run_tests.py        # Test runner
```

## Running Tests

### Method 1: Using Test Runner
```bash
python tests/run_tests.py
```

### Method 2: Using unittest
```bash
python -m unittest discover tests
```

### Method 3: Running Individual Test Files
```bash
python -m unittest tests.test_animals
python -m unittest tests.test_environment
python -m unittest tests.test_engine
python -m unittest tests.test_integration
```

## Test Coverage

### 1. Animal Class Tests (test_animals.py)
- ✅ Penguin creation and basic attributes
- ✅ Animal movement and boundary checks
- ✅ Energy consumption and recovery
- ✅ Breeding mechanism
- ✅ Death determination
- ✅ Distance calculation

### 2. Environment Class Tests (test_environment.py)
- ✅ Environment initialization
- ✅ Land/sea detection
- ✅ Ice thickness calculation
- ✅ Environment update (seasonal changes)

### 3. Simulation Engine Tests (test_engine.py)
- ✅ Engine initialization
- ✅ Tick and Step functionality
- ✅ State serialization
- ✅ Predation mechanism
- ✅ Breeding mechanism
- ✅ Environment update
- ✅ Dead animal removal

### 4. Integration Tests (test_integration.py)
- ✅ Complete simulation cycle
- ✅ State consistency
- ✅ JSON serialization
- ✅ Long-running stability

## Test Result Example

After running tests, you should see output similar to:

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

## Adding New Tests

1. Add new test methods in the corresponding test file
2. Test method names must start with `test_`
3. Use `self.assert*` methods for assertions
4. Run tests to verify new functionality

Example:
```python
def test_new_feature(self):
    """Test new feature"""
    # Arrange
    engine = SimulationEngine()
    
    # Act
    engine.step(10)
    
    # Assert
    state = engine.get_state()
    self.assertEqual(state.tick, 10)
```
