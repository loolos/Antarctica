#!/bin/bash
echo "Running Tests..."
echo ""

python3 tests/run_tests.py

if [ $? -eq 0 ]; then
    echo ""
    echo "All tests passed!"
else
    echo ""
    echo "Some tests failed. Check the output above."
fi

