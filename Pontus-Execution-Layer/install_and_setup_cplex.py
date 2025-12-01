#!/usr/bin/env python3
"""
Complete CPLEX Installation and Setup
Extracts, installs, and integrates CPLEX with OR-Tools as fallback
"""
import zipfile
import os
import sys
import subprocess
from pathlib import Path

def find_preview_folder():
    """Find Preview folder with CPLEX"""
    locations = [
        Path('/Users/arjundixit/Desktop/Preview'),
        Path('/Users/arjundixit/Downloads/PontusRouting/Preview'),
        Path('/Users/arjundixit/Downloads/Preview'),
    ]
    
    for loc in locations:
        if loc.exists():
            return loc
    return None

def extract_cplex_zip(zip_path, extract_to):
    """Extract CPLEX zip file"""
    print(f"📦 Extracting {zip_path.name}...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print("✅ Extraction complete!")
        return True
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return False

def find_cplex_python_dir(root_dir):
    """Find CPLEX Python installation directory"""
    for root, dirs, files in os.walk(root_dir):
        if 'setup.py' in files:
            path_str = str(root)
            if 'cplex' in path_str.lower() and 'python' in path_str.lower():
                # Prefer arm64_osx for M1/M2/M3 Macs
                if 'arm64_osx' in path_str:
                    return Path(root)
                elif 'x86-64_osx' in path_str:
                    return Path(root)
    return None

def install_cplex_python(cplex_dir):
    """Install CPLEX Python bindings"""
    print(f"\n📦 Installing CPLEX from: {cplex_dir}")
    
    try:
        os.chdir(cplex_dir)
        result = subprocess.run(
            [sys.executable, 'setup.py', 'install'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Installation successful!")
            return True
        else:
            print(f"⚠️  Installation output: {result.stdout}")
            print(f"⚠️  Errors: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Installation error: {e}")
        return False

def test_cplex():
    """Test CPLEX installation"""
    print("\n🧪 Testing CPLEX installation...")
    try:
        result = subprocess.run(
            [sys.executable, '-c', 'import cplex; print("CPLEX version:", cplex.__version__)'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✅ {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Import failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 CPLEX Installation and Setup")
    print("=" * 60)
    
    # Find Preview folder
    preview = find_preview_folder()
    if not preview:
        print("❌ Preview folder not found!")
        print("\nSearched in:")
        print("  - /Users/arjundixit/Desktop/Preview")
        print("  - /Users/arjundixit/Downloads/PontusRouting/Preview")
        print("  - /Users/arjundixit/Downloads/Preview")
        return 1
    
    print(f"✅ Found Preview folder: {preview}")
    
    # Extract to PontusRouting/cplex_extracted
    extract_to = Path('/Users/arjundixit/Downloads/PontusRouting/cplex_extracted')
    extract_to.mkdir(parents=True, exist_ok=True)
    
    # Find and extract zip files
    zip_files = list(preview.glob('*.zip'))
    if zip_files:
        print(f"\n📦 Found {len(zip_files)} zip file(s)")
        # Prefer ARM64 version
        arm64_zip = None
        for z in zip_files:
            if 'arm64' in z.name.lower():
                arm64_zip = z
                break
        
        if not arm64_zip and zip_files:
            arm64_zip = zip_files[0]  # Use first zip if no ARM64 found
        
        if arm64_zip:
            if not extract_cplex_zip(arm64_zip, extract_to):
                return 1
        else:
            print("❌ No zip files found to extract")
            return 1
    else:
        print("ℹ️  No zip files found - checking if already extracted...")
        # Check if CPLEX is already in Preview
        cplex_dir = find_cplex_python_dir(preview)
        if cplex_dir:
            print(f"✅ Found CPLEX in Preview: {cplex_dir}")
            if install_cplex_python(cplex_dir):
                return 0 if test_cplex() else 1
            return 1
    
    # Find CPLEX Python directory in extracted files
    print("\n🔍 Searching for CPLEX Python directory...")
    cplex_dir = find_cplex_python_dir(extract_to)
    
    if not cplex_dir:
        print("❌ Could not find CPLEX Python directory")
        print("\nTrying to find any setup.py files...")
        for root, dirs, files in os.walk(extract_to):
            if 'setup.py' in files:
                print(f"   Found: {root}")
        return 1
    
    print(f"✅ Found CPLEX Python directory: {cplex_dir}")
    
    # Install
    if install_cplex_python(cplex_dir):
        if test_cplex():
            print("\n" + "=" * 60)
            print("✅ CPLEX installation complete!")
            print("=" * 60)
            return 0
    
    return 1

if __name__ == '__main__':
    sys.exit(main())

