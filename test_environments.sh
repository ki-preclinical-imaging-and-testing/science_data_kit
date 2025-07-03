#!/bin/bash
echo "Testing Science Data Kit Environments"
echo "===================================="

echo ""
echo "Testing main environment..."
if [ -d "science-data-kit-env" ]; then
    source science-data-kit-env/bin/activate
    echo "Main environment Python: $(python --version)"
    echo "Main environment location: $(which python)"
    deactivate
else
    echo "Main environment not found!"
fi

echo ""
echo "Testing isatools environment..."
if [ -d "science-data-kit-isatools-env" ]; then
    source science-data-kit-isatools-env/bin/activate
    echo "isatools environment Python: $(python --version)"
    echo "isatools environment location: $(which python)"
    deactivate
else
    echo "isatools environment not found!"
fi

echo ""
echo "Current system Python: $(python3 --version 2>/dev/null || echo 'Not found')"
echo "Current system location: $(which python3 2>/dev/null || echo 'Not found')"
