# CPLEX Quick Start Guide

## ⚠️ IMPORTANT: You Don't Need CPLEX Right Now!

**Good news**: Your routing engine works perfectly with **OR-Tools only**. CPLEX is optional and only needed for very advanced optimization.

**You can skip CPLEX installation** and use the system as-is. OR-Tools handles everything you need for Phase 1.

---

## If You Still Want to Install CPLEX

### Step 1: Download CPLEX

1. Go to: https://www.ibm.com/products/ilog-cplex-optimization-studio
2. Click "Download" or "Get Started"
3. Sign up for a free IBM account (if needed)
4. Download **CPLEX Optimization Studio Community Edition** (it's free)
5. For macOS, download the **macOS** version (usually a `.tar.gz` or `.dmg` file)

### Step 2: Extract the File

**If you have a `.tar.gz` file:**
```bash
cd ~/Downloads
tar -xzf cplex*.tar.gz
```

**If you have a `.zip` file:**
```bash
cd ~/Downloads
unzip cplex*.zip
```

**If you have a `.dmg` file:**
- Double-click it in Finder
- It will mount as a disk
- Drag the CPLEX folder to Applications or Desktop

### Step 3: Find the Python Installation Directory

After extraction, look for:
```
CPLEX_Studio<version>/
  └── cplex/
      └── python/
          └── <version>/
              └── <platform>/  ← You need this folder
                  └── setup.py
```

For Python 3.13 on macOS ARM64 (M1/M2/M3 Mac), you need:
- Platform folder: `arm64_osx` or `x86-64_osx`

### Step 4: Install Python Bindings

```bash
# Navigate to the platform folder
cd ~/Downloads/CPLEX_Studio*/cplex/python/*/arm64_osx

# Install
python3 setup.py install

# Or if that doesn't work, try:
python3.12 setup.py install  # CPLEX might not support Python 3.13 yet
```

### Step 5: Verify

```bash
python3 -c "import cplex; print('Success! CPLEX version:', cplex.__version__)"
```

---

## Common Issues

### Issue: "Can't find the downloaded file"
**Solution**: 
- Check your browser's Downloads folder
- Check if it's still downloading
- Re-download from IBM website

### Issue: "Wrong Python version"
**Solution**: CPLEX might not support Python 3.13 yet. Try:
```bash
# Check available Python versions
which python3.12 python3.11 python3.10

# Use an older Python version
python3.12 setup.py install
```

### Issue: "No module named cplex" after installation
**Solution**: 
- Make sure you installed to the correct Python
- Try: `pip3 install cplex` (if available)
- Or use virtual environment

---

## Alternative: Use pip (Easier!)

Some CPLEX versions can be installed directly via pip:

```bash
pip3 install cplex
```

**Note**: This might not work for all platforms, but it's worth trying first!

---

## Recommendation

**For now, skip CPLEX installation** and use OR-Tools. You can always add CPLEX later when you need advanced optimization.

Your current setup is perfect for:
- ✅ Phase 1 (Comparison tool)
- ✅ Multi-route optimization
- ✅ Fast route finding
- ✅ All your initial needs

CPLEX is only needed for:
- Very large route graphs (1000+ segments)
- Complex constraint optimization
- Enterprise-scale routing

---

## Quick Test (Without CPLEX)

Test that your routing engine works without CPLEX:

```bash
cd ~/Downloads/PontusRouting
python3 -c "from app.services.routing_service import RoutingService; print('Routing service works!')"
```

If this works, you're all set! 🎉

