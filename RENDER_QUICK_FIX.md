# Quick Fix for Render Deployment

## Current Issue
The app can't find the `app` module because uvicorn is running from the wrong directory.

## Solution: Update Start Command in Render

Go to your Render service settings and update:

### Start Command:
```bash
cd Pontus-Execution-Layer && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Build Command (if not already set):
```bash
cd Pontus-Execution-Layer && pip install -r requirements.txt
```

### OR Set Root Directory (Alternative)

If you prefer, set **Root Directory** to `Pontus-Execution-Layer` and use:

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Why This Works

The `app` module is located in `Pontus-Execution-Layer/app/`, so uvicorn needs to run from that directory (or have it set as the root directory) to find the module.

