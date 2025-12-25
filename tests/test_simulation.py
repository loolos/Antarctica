"""
Test simulation core
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

from simulation.engine import SimulationEngine

def test_simulation():
    """Test simulation engine"""
    print("Initializing simulation engine...")
    engine = SimulationEngine()
    
    print(f"Initial state:")
    state = engine.get_state()
    print(f"  Tick: {state.tick}")
    print(f"  Penguins: {len(state.penguins)}")
    print(f"  Seals: {len(state.seals)}")
    print(f"  Fish: {len(state.fish)}")
    print(f"  Temperature: {state.environment.temperature}°C")
    print(f"  Ice Coverage: {state.environment.ice_coverage * 100:.1f}%")
    
    print("\nRunning 100 steps...")
    engine.step(100)
    
    state = engine.get_state()
    print(f"\nState after 100 steps:")
    print(f"  Tick: {state.tick}")
    print(f"  Penguins: {len(state.penguins)}")
    print(f"  Seals: {len(state.seals)}")
    print(f"  Fish: {len(state.fish)}")
    print(f"  Temperature: {state.environment.temperature}°C")
    print(f"  Ice Coverage: {state.environment.ice_coverage * 100:.1f}%")
    
    print("\nTesting state serialization...")
    state_dict = state.to_dict()
    print(f"  Serialization successful, contains {len(state_dict)} keys")
    print(f"  Penguin data: {len(state_dict['penguins'])} entries")
    
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    test_simulation()

