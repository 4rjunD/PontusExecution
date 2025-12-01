# CPLEX Manual Installation Guide

## If You Already Have a CPLEX Folder

If you've already extracted CPLEX as a folder in your workspace, follow these steps:

### Step 1: Find the CPLEX Python Directory

The CPLEX Python bindings are usually located at:
```
CPLEX_Studio<version>/cplex/python/<version>/<platform>/
```

For macOS ARM64 (M1/M2/M3 Mac), you need:
- Platform: `arm64_osx` or `x86-64_osx`

### Step 2: Navigate to the Python Directory

```bash
cd /Users/arjundixit/Downloads/PontusRouting
# Find the CPLEX folder - replace with your actual folder name
cd <CPLEX_FOLDER_NAME>/cplex/python/*/arm64_osx
# Or if it's x86-64:
# cd <CPLEX_FOLDER_NAME>/cplex/python/*/x86-64_osx
```

### Step 3: Install Python Bindings

```bash
python3 setup.py install
```

### Step 4: Verify Installation

```bash
python3 -c "import cplex; print('CPLEX version:', cplex.__version__)"
```

---

## If You Need to Extract from Zip

### Step 1: Extract the Zip File

```bash
cd /Users/arjundixit/Downloads/PontusRouting
unzip /Users/arjundixit/Desktop/Preview/cos_installer_preview-22.1.2.R13-M0XN1ML-osx-arm64.zip
```

### Step 2: Find the Python Directory

```bash
find . -name "setup.py" -path "*/cplex/python/*/arm64_osx/*" 2>/dev/null
```

### Step 3: Install

```bash
cd <path_from_step_2>
python3 setup.py install
```

---

## Quick Installation Script

Run this script I created:

```bash
cd /Users/arjundixit/Downloads/PontusRouting
python3 install_cplex.py
```

This script will:
1. Extract the zip file
2. Find the CPLEX Python directory
3. Install the Python bindings
4. Test the installation

---

## Troubleshooting

### Problem: "No module named cplex" after installation
**Solution**: Make sure you installed to the correct Python version:
```bash
which python3
python3 -c "import sys; print(sys.executable)"
```

### Problem: Wrong platform (not arm64_osx)
**Solution**: Check what platforms are available:
```bash
ls <CPLEX_FOLDER>/cplex/python/*/
```

### Problem: Python 3.13 not supported
**Solution**: CPLEX might not support Python 3.13 yet. Try:
```bash
python3.12 setup.py install
# or
python3.11 setup.py install
```

---

## After Installation

Once CPLEX is installed, enable it in your routing service:

Edit `app/main.py` line 34:
```python
routing_service = RoutingService(use_cplex=True)  # Changed from False
```

Or pass it in API requests:
```bash
curl "http://localhost:8000/api/routes/optimize?from_asset=USD&to_asset=EUR&use_cplex=true"
```

---

## Need Help?

If you have the CPLEX folder already extracted, tell me:
1. The folder name/path
2. I'll help you find the Python directory and install it

