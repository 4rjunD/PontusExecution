# CPLEX Installation Guide for macOS

## Step 1: Find Your CPLEX Download

The CPLEX download from IBM usually comes as:
- A `.tar.gz` file (most common for macOS/Linux)
- A `.dmg` file (macOS installer)
- A `.zip` file

Let's find it:

```bash
# Check Downloads folder
ls -lh ~/Downloads/*.tar.gz ~/Downloads/*.dmg ~/Downloads/*.zip | grep -i cplex

# Or search for recent large files (CPLEX is usually 100MB+)
ls -lht ~/Downloads/ | head -10
```

## Step 2: Extract the File

### If it's a .tar.gz file:
```bash
cd ~/Downloads
tar -xzf cplex*.tar.gz
```

### If it's a .zip file:
```bash
cd ~/Downloads
unzip cplex*.zip
```

### If it's a .dmg file:
Double-click it in Finder, or:
```bash
cd ~/Downloads
open cplex*.dmg
```

## Step 3: Locate the Extracted Folder

After extraction, you should see a folder like:
- `cplex` or `CPLEX_Studio*` or `ILOG_CPLEX*`

Find it:
```bash
cd ~/Downloads
ls -la | grep -i cplex
```

## Step 4: Install CPLEX Python Bindings

Once you find the extracted folder, navigate to the Python directory:

```bash
# Find the CPLEX installation
cd ~/Downloads
find . -name "setup.py" -path "*/cplex/python/*" 2>/dev/null

# Or manually navigate (typical structure):
# CPLEX_Studio<version>/cplex/python/<version>/<platform>/
```

For Python 3.13 on macOS ARM64, you'll need:
- Platform: `arm64_osx` or `x86-64_osx` (depending on your Mac)

## Step 5: Install Python Package

```bash
# Navigate to the Python directory
cd ~/Downloads/CPLEX_Studio*/cplex/python/*/arm64_osx  # or x86-64_osx

# Install
python3 setup.py install
```

## Alternative: Use pip (if available)

Some CPLEX versions can be installed via pip:
```bash
pip3 install cplex
```

## Step 6: Verify Installation

```bash
python3 -c "import cplex; print('CPLEX version:', cplex.__version__)"
```

## Troubleshooting

### Problem: Can't find the zip file
**Solution**: 
1. Check your browser's download history
2. Check if it's in a different location:
   ```bash
   find ~ -name "*cplex*" -type f 2>/dev/null | head -10
   ```

### Problem: Zip file won't extract
**Solution**:
```bash
# Try with verbose output
unzip -v cplex*.zip

# Or use Archive Utility (double-click in Finder)
```

### Problem: Wrong Python version/platform
**Solution**: CPLEX might not have Python 3.13 bindings yet. Try:
```bash
# Check what Python versions are available
ls ~/Downloads/CPLEX_Studio*/cplex/python/

# You might need to use Python 3.11 or 3.12
python3.12 -c "import cplex"
```

### Problem: Permission denied
**Solution**:
```bash
# Make sure you have write permissions
sudo python3 setup.py install
```

## Quick Check Script

Run this to see what you have:
```bash
echo "=== Checking Downloads ==="
ls -lh ~/Downloads/*.{zip,tar.gz,dmg} 2>/dev/null | grep -i -E "cplex|ilog|ibm" || echo "No CPLEX files found in Downloads"

echo -e "\n=== Checking for extracted CPLEX ==="
find ~/Downloads -maxdepth 2 -type d -iname "*cplex*" -o -iname "*ilog*" 2>/dev/null

echo -e "\n=== Python version ==="
python3 --version

echo -e "\n=== Checking if CPLEX already installed ==="
python3 -c "import cplex; print('CPLEX installed:', cplex.__version__)" 2>/dev/null || echo "CPLEX not installed"
```

