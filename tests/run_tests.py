"""
Run all tests
"""
import unittest
import sys
import os
import io

# Removed manual encoding override to prevent conflicts

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def run_all_tests():
    """Run all tests"""
    # Discover and load all tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailed tests:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\nErrored tests:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    print("="*60)
    
    # Return whether all passed
    return len(result.failures) == 0 and len(result.errors) == 0

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)

