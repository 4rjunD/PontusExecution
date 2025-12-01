# Install CPLEX from Preview Folder - Quick Guide

## Step 1: Run the Installation Script

I've created a script that will automatically find and install CPLEX from your Preview folder.

**Run this command:**

```bash
cd /Users/arjundixit/Downloads/PontusRouting
./setup_cplex_from_preview.sh
```

This script will:
1. ✅ Find the Preview folder
2. ✅ Extract any zip files if needed
3. ✅ Find the CPLEX Python directory
4. ✅ Install the Python bindings
5. ✅ Test the installation

---

## Step 2: Manual Installation (if script doesn't work)

### Find the CPLEX Python Directory

```bash
# Navigate to Preview folder (adjust path if needed)
cd /Users/arjundixit/Desktop/Preview
# or
cd /Users/arjundixit/Downloads/PontusRouting/Preview

# Find setup.py in CPLEX Python directory
find . -name "setup.py" -path "*/cplex/python/*" | head -1
```

### Extract Zip File (if needed)

If Preview contains zip files that need extraction:

```bash
cd /Users/arjundixit/Desktop/Preview  # or wherever Preview is
unzip cos_installer_preview-22.1.2.R13-M0XN1ML-osx-arm64.zip
```

### Install Python Bindings

Once you find the directory with `setup.py`:

```bash
cd <path_to_setup.py_directory>
python3 setup.py install
```

### Verify Installation

```bash
python3 -c "import cplex; print('CPLEX version:', cplex.__version__)"
```

---

## Step 3: Enable CPLEX in Your App

After installation, edit `app/main.py` line 34:

```python
routing_service = RoutingService(use_cplex=True)  # Changed from False
```

---

## Troubleshooting

### "Preview folder not found"
**Solution**: Tell me the exact path to your Preview folder and I'll update the script.

### "No setup.py found"
**Solution**: The zip file might need to be extracted first. Run:
```bash
cd <Preview_folder>
unzip *.zip
```

### "Wrong Python version"
**Solution**: CPLEX might not support Python 3.13. Try:
```bash
python3.12 setup.py install
# or
python3.11 setup.py install
```

### "Permission denied"
**Solution**: 
```bash
sudo python3 setup.py install
```

---

## Quick Test

After installation, test that everything works:

```bash
cd /Users/arjundixit/Downloads/PontusRouting
python3 -c "from app.services.cplex_solver import CPLEX_AVAILABLE; print('CPLEX available:', CPLEX_AVAILABLE)"
```

If it prints `CPLEX available: True`, you're all set! 🎉

