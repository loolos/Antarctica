#!/bin/bash
echo "Running Tests..."
echo ""

# Change to project root directory
cd "$(dirname "$0")/.."
python3 tests/run_tests.py

if [ $? -eq 0 ]; then
    echo ""
    echo "All tests passed!"
else
    echo ""
    echo "Some tests failed. Check the output above."
fi

