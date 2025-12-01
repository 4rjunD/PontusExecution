# Routing Engine Setup Guide

This guide explains how to set up the routing engine components, including OR-Tools and CPLEX.

## Quick Start (OR-Tools Only)

The routing engine works out of the box with OR-Tools. No additional setup required!

```bash
pip install -r requirements.txt
```

OR-Tools will be installed automatically via pip.

## CPLEX Setup (Optional - Advanced Optimization)

CPLEX provides more advanced optimization capabilities but requires separate installation.

### Option 1: CPLEX Community Edition (Free)

1. **Download CPLEX Community Edition:**
   - Visit: https://www.ibm.com/products/ilog-cplex-optimization-studio
   - Sign up for a free account
   - Download CPLEX Optimization Studio Community Edition
   - Install it on your system

2. **Install Python API:**
   ```bash
   # On macOS/Linux, CPLEX is typically installed at:
   # /opt/ibm/ILOG/CPLEX_Studio<version>/cplex/python/<version>/<platform>
   
   # Navigate to the CPLEX Python directory
   cd /opt/ibm/ILOG/CPLEX_Studio<version>/cplex/python/<version>/<platform>
   
   # Install CPLEX Python package
   python setup.py install
   ```

3. **Verify Installation:**
   ```python
   python -c "import cplex; print('CPLEX installed successfully')"
   ```

4. **Enable CPLEX in the application:**
   - Edit `app/main.py`
   - Change `RoutingService(use_cplex=False)` to `RoutingService(use_cplex=True)`
   - Or pass `use_cplex=true` in API requests

### Option 2: CPLEX via pip (Limited)

For some platforms, CPLEX may be available via pip, but this is limited:
```bash
pip install cplex
```

**Note:** The pip version may have limitations. The full Community Edition is recommended.

### Troubleshooting CPLEX

If CPLEX is not installed, the routing engine will:
- Automatically fall back to OR-Tools
- Log a warning message
- Continue to work normally

The application is designed to work without CPLEX - it's an optional enhancement.

## Testing the Setup

1. **Start the application:**
   ```bash
   python -m app.main
   ```

2. **Test OR-Tools routing:**
   ```bash
   curl "http://localhost:8000/api/routes/optimize?from_asset=USD&to_asset=EUR"
   ```

3. **Test with CPLEX (if installed):**
   ```bash
   curl "http://localhost:8000/api/routes/optimize?from_asset=USD&to_asset=EUR&use_cplex=true"
   ```

## What Each Solver Provides

### OR-Tools (Always Available)
- ✅ Shortest path optimization
- ✅ Multi-weight path finding
- ✅ Constraint-based routing
- ✅ Multi-objective optimization
- ✅ Fast and reliable

### CPLEX (Optional)
- ✅ Mixed-integer programming
- ✅ Advanced constraint handling
- ✅ Better scalability for large graphs
- ✅ More sophisticated optimization algorithms

## System Requirements

- **OR-Tools:** Works on all platforms (Windows, macOS, Linux)
- **CPLEX Community Edition:**
  - Available for Windows, macOS, Linux
  - Free for academic and small commercial use
  - Requires IBM account registration

## Next Steps

Once setup is complete, see the API documentation at `http://localhost:8000/docs` for routing endpoints.

