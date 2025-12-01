#!/usr/bin/env python3
"""
CPLEX Installation Script
Extracts and installs CPLEX Python bindings
"""
import zipfile
import os
import sys
import subprocess
from pathlib import Path

# Paths
zip_path = Path('/Users/arjundixit/Desktop/Preview/cos_installer_preview-22.1.2.R13-M0XN1ML-osx-arm64.zip')
extract_to = Path('/Users/arjundixit/Downloads/PontusRouting/cplex_extracted')

def find_cplex_python_dir(root_dir):
    """Find CPLEX Python installation directory"""
    for root, dirs, files in os.walk(root_dir):
        if 'setup.py' in files:
            path = Path(root)
            if 'cplex' in str(path).lower() and 'python' in str(path).lower():
                # Check for arm64_osx or x86-64_osx
                if 'arm64_osx' in str(path) or 'x86-64_osx' in str(path):
                    return path
    return None

def main():
    print("🔍 CPLEX Installation Script")
    print("=" * 50)
    
    # Check if zip exists
    if not zip_path.exists():
        print(f"❌ Error: Zip file not found at {zip_path}")
        print("\nPlease check the path to your CPLEX zip file.")
        return 1
    
    print(f"✅ Found zip file: {zip_path}")
    print(f"📦 Extracting to: {extract_to}")
    
    # Create extraction directory
    extract_to.mkdir(parents=True, exist_ok=True)
    
    # Extract zip
    try:
        print("\n📂 Extracting files...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            file_count = len(zip_ref.namelist())
            print(f"   Found {file_count} files in archive")
            zip_ref.extractall(extract_to)
        print("✅ Extraction complete!")
    except Exception as e:
        print(f"❌ Error extracting: {e}")
        return 1
    
    # Find CPLEX Python directory
    print("\n🔍 Searching for CPLEX Python directory...")
    python_dir = find_cplex_python_dir(extract_to)
    
    if not python_dir:
        print("❌ Could not find CPLEX Python directory")
        print("\nTrying to find any setup.py files...")
        for root, dirs, files in os.walk(extract_to):
            if 'setup.py' in files:
                print(f"   Found: {root}")
        return 1
    
    print(f"✅ Found CPLEX Python directory: {python_dir}")
    
    # Check Python version
    python_version = sys.version_info
    print(f"\n🐍 Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Install
    print(f"\n📦 Installing CPLEX Python bindings...")
    print(f"   Directory: {python_dir}")
    
    try:
        os.chdir(python_dir)
        result = subprocess.run(
            [sys.executable, 'setup.py', 'install'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Installation successful!")
            print("\n🧪 Testing installation...")
            test_result = subprocess.run(
                [sys.executable, '-c', 'import cplex; print("CPLEX version:", cplex.__version__)'],
                capture_output=True,
                text=True
            )
            if test_result.returncode == 0:
                print(test_result.stdout)
                print("✅ CPLEX is ready to use!")
                return 0
            else:
                print("⚠️  Installation completed but import test failed:")
                print(test_result.stderr)
                return 1
        else:
            print("❌ Installation failed:")
            print(result.stderr)
            return 1
    except Exception as e:
        print(f"❌ Error during installation: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())

