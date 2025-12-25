
import sys
import os

# Add project root to path (parent directory of tests/)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from simulation.animals import Penguin

def check_alive():
    print("Checking Penguin.is_alive logic...")
    
    # Case 1: Energy 0
    p1 = Penguin(id="p1", x=0, y=0, energy=0)
    print(f"p1: energy={p1.energy}, age={p1.age}, max_age={p1.max_age}")
    alive1 = p1.is_alive()
    print(f"p1.is_alive() = {alive1} (Expected: False)")
    
    # Case 2: Age > Max Age
    p2 = Penguin(id="p2", x=0, y=0, energy=50, age=2000)
    print(f"p2: energy={p2.energy}, age={p2.age}, max_age={p2.max_age}")
    alive2 = p2.is_alive()
    print(f"p2.is_alive() = {alive2} (Expected: False)")

    if alive1 or alive2:
        print("FAIL: is_alive returned available True when it should be False")
        sys.exit(1)
    else:
        print("PASS: Logic seems correct")
        sys.exit(0)

if __name__ == "__main__":
    check_alive()
