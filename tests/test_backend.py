"""
Test backend server startup
"""
import sys
import os
import io
import subprocess
import time
import urllib.request
import json

# Set UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_backend():
    """Test backend server"""
    print("="*60)
    print("Testing backend server")
    print("="*60)
    
    # Check backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    if not os.path.exists(backend_dir):
        print("❌ backend directory does not exist")
        return False
    
    # Check main.py
    main_py = os.path.join(backend_dir, 'main.py')
    if not os.path.exists(main_py):
        print("❌ main.py does not exist")
        return False
    
    print("✅ File check passed")
    
    # Check dependencies
    print("\nChecking Python modules...")
    try:
        # Add project root to path
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, project_root)
        from simulation.engine import SimulationEngine
        print("✅ simulation module imported successfully")
    except Exception as e:
        print(f"❌ simulation module import failed: {e}")
        return False
    
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI and Uvicorn are installed")
    except ImportError as e:
        print(f"❌ Dependencies not installed: {e}")
        print("   Please run: cd backend && py -m pip install -r requirements.txt")
        return False
    
    # Try importing main
    print("\nTesting main.py import...")
    try:
        sys.path.insert(0, backend_dir)
        import main
        print("✅ main.py imported successfully")
        print(f"   FastAPI app: {main.app.title}")
    except Exception as e:
        print(f"❌ main.py import failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "="*60)
    print("✅ Backend server configuration check passed!")
    print("="*60)
    print("\nStartup instructions:")
    print("1. Open terminal, navigate to backend directory")
    print("2. Run: py main.py")
    print("3. Or double-click: start_backend.bat")
    print("\nServer will start at http://localhost:8000")
    print("API docs: http://localhost:8000/docs")
    print("="*60)
    
    return True

if __name__ == "__main__":
    success = test_backend()
    sys.exit(0 if success else 1)

