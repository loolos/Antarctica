"""
Quick test script - verify core functionality
"""
import sys
import os
import io

# Set UTF-8 encoding (Windows compatible)
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add project root to path (parent directory of tests/)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_imports():
    """Test module imports"""
    print("Testing module imports...")
    try:
        from simulation.engine import SimulationEngine
        from simulation.animals import Penguin, Seal, Fish
        from simulation.environment import Environment
        from simulation.world import WorldState
        print("✅ All modules imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_engine_basic():
    """Test engine basic functionality"""
    print("\nTesting engine basic functionality...")
    try:
        from simulation.engine import SimulationEngine
        
        engine = SimulationEngine()
        state = engine.get_state()
        
        print(f"  ✅ Engine initialized successfully")
        print(f"  - Initial Tick: {state.tick}")
        print(f"  - Penguins: {len(state.penguins)}")
        print(f"  - Seals: {len(state.seals)}")
        print(f"  - Fish: {len(state.fish)}")
        
        # Test tick
        engine.tick()
        new_state = engine.get_state()
        assert new_state.tick == 1, "Tick should increase"
        print(f"  ✅ Tick functionality normal")
        
        # Test step
        engine.step(10)
        new_state = engine.get_state()
        assert new_state.tick == 11, "Step should advance multiple steps"
        print(f"  ✅ Step functionality normal")
        
        return True
    except Exception as e:
        print(f"  ❌ Engine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_animals():
    """Test animal classes"""
    print("\nTesting animal classes...")
    try:
        from simulation.animals import Penguin, Seal, Fish
        
        # Test penguin
        penguin = Penguin(id="test", x=100, y=100, energy=80)
        assert penguin.is_alive(), "Penguin should be alive"
        penguin.tick()
        assert penguin.energy < 80, "Tick should consume energy"
        print(f"  ✅ Penguin class normal")
        
        # Test seal
        seal = Seal(id="test", x=200, y=200, energy=100)
        assert seal.is_alive(), "Seal should be alive"
        print(f"  ✅ Seal class normal")
        
        # Test fish
        fish = Fish(id="test", x=300, y=300, energy=30)
        assert fish.is_alive(), "Fish should be alive"
        print(f"  ✅ Fish class normal")
        
        return True
    except Exception as e:
        print(f"  ❌ Animal test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment():
    """Test environment class"""
    print("\nTesting environment class...")
    try:
        from simulation.environment import Environment
        
        env = Environment(width=800, height=600)
        assert env.width == 800, "Width should be correct"
        assert env.height == 600, "Height should be correct"
        assert 0 <= env.ice_coverage <= 1, "Ice coverage should be between 0-1"
        print(f"  ✅ Environment initialization normal")
        
        # Test land detection - use actual ice floe positions
        # Since ice floes are randomly generated, test with known positions
        if env.ice_floes:
            # Test with first ice floe center (should be land)
            floe = env.ice_floes[0]
            assert env.is_land(floe['x'], floe['y']), "Ice floe center should be land"
            # Test position far from all floes (should be sea)
            assert not env.is_land(750, 550), "Position far from floes should be sea"
        else:
            # If no ice floes, all positions should be sea
            assert not env.is_land(100, 300), "Without ice floes, should be sea"
        print(f"  ✅ Land/sea detection normal")
        
        # Test tick
        initial_temp = env.temperature
        env.tick()
        print(f"  ✅ Environment update normal (temperature: {initial_temp} -> {env.temperature})")
        
        return True
    except Exception as e:
        print(f"  ❌ Environment test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_serialization():
    """Test serialization"""
    print("\nTesting state serialization...")
    try:
        from simulation.engine import SimulationEngine
        import json
        
        engine = SimulationEngine()
        engine.step(5)
        state = engine.get_state()
        
        # Test to_dict
        state_dict = state.to_dict()
        assert 'tick' in state_dict, "Should contain tick"
        assert 'penguins' in state_dict, "Should contain penguins"
        assert 'seals' in state_dict, "Should contain seals"
        assert 'fish' in state_dict, "Should contain fish"
        assert 'environment' in state_dict, "Should contain environment"
        print(f"  ✅ to_dict() normal")
        
        # Test JSON serialization
        json_str = json.dumps(state_dict)
        assert isinstance(json_str, str), "Should be string"
        print(f"  ✅ JSON serialization normal")
        
        # Test JSON deserialization
        parsed = json.loads(json_str)
        assert parsed['tick'] == state.tick, "Tick should match"
        print(f"  ✅ JSON deserialization normal")
        
        return True
    except Exception as e:
        print(f"  ❌ Serialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simulation_run():
    """Test simulation run"""
    print("\nTesting simulation run...")
    try:
        from simulation.engine import SimulationEngine
        
        engine = SimulationEngine()
        initial_counts = {
            'penguins': len(engine.get_state().penguins),
            'seals': len(engine.get_state().seals),
            'fish': len(engine.get_state().fish),
        }
        
        print(f"  Initial counts: Penguins={initial_counts['penguins']}, "
              f"Seals={initial_counts['seals']}, Fish={initial_counts['fish']}")
        
        # Run 100 steps
        engine.step(100)
        
        state = engine.get_state()
        final_counts = {
            'penguins': len(state.penguins),
            'seals': len(state.seals),
            'fish': len(state.fish),
        }
        
        print(f"  After 100 steps: Penguins={final_counts['penguins']}, "
              f"Seals={final_counts['seals']}, Fish={final_counts['fish']}")
        print(f"  Tick: {state.tick}")
        print(f"  Temperature: {state.environment.temperature:.1f}°C")
        print(f"  Ice Coverage: {state.environment.ice_coverage * 100:.1f}%")
        
        # Verify system is still running
        assert state.tick == 100, "Tick should be 100"
        assert state.environment is not None, "Environment should exist"
        
        print(f"  ✅ Simulation run normal")
        
        return True
    except Exception as e:
        print(f"  ❌ Simulation run test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("Antarctic Ecosystem Simulation - Quick Test")
    print("="*60)
    
    tests = [
        ("Module Import", test_imports),
        ("Engine Basic", test_engine_basic),
        ("Animal Classes", test_animals),
        ("Environment Class", test_environment),
        ("State Serialization", test_serialization),
        ("Simulation Run", test_simulation_run),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} test exception: {e}")
            results.append((name, False))
    
    # Print summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ Passed" if result else "❌ Failed"
        print(f"{name}: {status}")
    
    print(f"\nTotal: {passed}/{total} passed")
    print("="*60)
    
    if passed == total:
        print("\n🎉 All tests passed! System running normally.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} tests failed, please check the output above.")
        return 1

if __name__ == "__main__":
    exit(main())
