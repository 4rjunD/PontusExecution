#!/usr/bin/env python3
"""Find CPLEX in Preview folder"""
import os
from pathlib import Path

# Check multiple possible locations
locations = [
    '/Users/arjundixit/Downloads/PontusRouting/Preview',
    '/Users/arjundixit/Desktop/Preview',
    '/Users/arjundixit/Downloads/Preview',
]

print("🔍 Searching for Preview folder with CPLEX...")
print("=" * 60)

for location in locations:
    path = Path(location)
    if path.exists():
        print(f"\n✅ Found: {location}")
        print(f"   Type: {'Directory' if path.is_dir() else 'File'}")
        
        # List contents
        try:
            items = list(path.iterdir())
            print(f"   Contents ({len(items)} items):")
            for item in items[:10]:
                print(f"      - {item.name} ({'dir' if item.is_dir() else 'file'})")
            if len(items) > 10:
                print(f"      ... and {len(items) - 10} more")
        except Exception as e:
            print(f"   Error reading: {e}")
        
        # Search for CPLEX
        print(f"\n   🔍 Searching for CPLEX...")
        cplex_paths = []
        for root, dirs, files in os.walk(path):
            # Look for CPLEX directories
            if any('cplex' in d.lower() or 'ilog' in d.lower() for d in dirs):
                for d in dirs:
                    if 'cplex' in d.lower() or 'ilog' in d.lower():
                        cplex_paths.append(os.path.join(root, d))
            
            # Look for setup.py in python directories
            if 'setup.py' in files and 'python' in root.lower():
                if 'cplex' in root.lower():
                    print(f"      ✅ Found CPLEX Python setup.py: {root}")
                    # Check for platform
                    if 'arm64' in root or 'x86-64' in root:
                        print(f"         🎯 This looks like the installation directory!")
                        print(f"         📦 To install, run:")
                        print(f"            cd {root}")
                        print(f"            python3 setup.py install")
        
        if cplex_paths:
            print(f"\n   Found {len(cplex_paths)} CPLEX-related directories:")
            for p in cplex_paths[:5]:
                print(f"      - {p}")
    else:
        print(f"\n❌ Not found: {location}")

print("\n" + "=" * 60)
print("💡 If you found the CPLEX Python directory, navigate to it and run:")
print("   python3 setup.py install")

