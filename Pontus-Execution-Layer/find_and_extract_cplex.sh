#!/bin/bash
# Helper script to find and extract CPLEX

echo "🔍 Searching for CPLEX files..."
echo ""

# Search for CPLEX files
echo "=== Checking Downloads folder ==="
find ~/Downloads -maxdepth 1 -type f \( -iname "*cplex*" -o -iname "*ilog*" -o -iname "*ibm*optimization*" \) 2>/dev/null

echo ""
echo "=== Checking for large recent files (CPLEX is usually 100MB+) ==="
ls -lht ~/Downloads/*.{zip,tar.gz,dmg} 2>/dev/null | head -5

echo ""
echo "=== Checking if already extracted ==="
find ~/Downloads -maxdepth 2 -type d \( -iname "*cplex*" -o -iname "*ilog*" \) 2>/dev/null

echo ""
echo "=== Instructions ==="
echo "1. If you found a .zip file, extract it with:"
echo "   cd ~/Downloads && unzip <filename>.zip"
echo ""
echo "2. If you found a .tar.gz file, extract it with:"
echo "   cd ~/Downloads && tar -xzf <filename>.tar.gz"
echo ""
echo "3. If you found a .dmg file, double-click it in Finder"
echo ""
echo "4. After extraction, look for: CPLEX_Studio*/cplex/python/*/arm64_osx/setup.py"
echo ""
echo "💡 TIP: You don't need CPLEX right now! OR-Tools works perfectly."
echo "   Install dependencies first: pip3 install -r requirements.txt"

