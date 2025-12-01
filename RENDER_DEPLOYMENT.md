# Render Deployment Configuration

## Render Web Service Configuration

### Basic Settings

**Service Type:** Web Service  
**Name:** PontusExecution  
**Environment:** Production  
**Language:** Python 3  
**Branch:** main  
**Region:** Oregon (US West)  
**Root Directory:** `Pontus-Execution-Layer` ⚠️ **IMPORTANT: Set this!**

### Build & Start Commands

**Option 1: Using Root Directory (Recommended)**

**Root Directory:** `Pontus-Execution-Layer`

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
cd Pontus-Execution-Layer && ./start.sh
```

**OR (if start.sh doesn't work):**
```bash
cd Pontus-Execution-Layer && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**OR (simplest - if Root Directory is set):**
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Option 2: Without Root Directory**

**Root Directory:** (leave empty)

**Build Command:**
```bash
cd Pontus-Execution-Layer && pip install -r requirements.txt
```

**Start Command:**
```bash
cd Pontus-Execution-Layer && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

> **Note:** Render automatically sets the `$PORT` environment variable. Do not hardcode a port number.

### Instance Type

**Recommended:** Standard ($25/month) or Starter ($7/month) for testing
- **Starter:** 512 MB RAM, 0.5 CPU (minimum for production)
- **Standard:** 2 GB RAM, 1 CPU (recommended for production workloads)

### Python Version

**IMPORTANT:** In Render dashboard, manually set Python version to **3.12** (not 3.13).

Render may not automatically read `runtime.txt`, so you need to:
1. Go to your service settings
2. Find "Python Version" or "Environment" section
3. Select **Python 3.12** (or specify `3.12.7`)

Alternatively, add this environment variable:
```
PYTHON_VERSION=3.12.7
```

### Environment Variables

Add these environment variables in Render's dashboard:

#### Required (Database & Redis)

```bash
# PostgreSQL Database URL
# Render will provide this if you create a PostgreSQL database service
# Format: postgresql+asyncpg://user:password@host:port/dbname
DATABASE_URL=postgresql+asyncpg://[your-render-postgres-url]

# Redis URL
# Render will provide this if you create a Redis service
# Format: redis://host:port/0
REDIS_URL=redis://[your-render-redis-url]

# Execution Mode (set to simulation for safety)
EXECUTION_MODE=simulation
```

#### Optional (API Keys - Add as needed)

```bash
# API Authentication (set to true in production)
REQUIRE_API_KEY=false

# CORS Origins (comma-separated or * for all)
CORS_ORIGINS=*

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Optional API Keys (only add if you have them)
EXCHANGERATE_API_KEY=
ETHERSCAN_API_KEY=
POLYGONSCAN_API_KEY=
COINGECKO_API_KEY=
SOCKET_API_KEY=
LIFI_API_KEY=
TRANSAK_API_KEY=
ONMETA_API_KEY=
ZEROX_API_KEY=

# Execution Layer API Keys (only if using real execution)
WISE_API_KEY=
WISE_API_EMAIL=
KRAKEN_API_KEY=
KRAKEN_PRIVATE_KEY=
```

## Step-by-Step Deployment

### 1. Create PostgreSQL Database (Required)

1. In Render dashboard, click **"New +"** → **"PostgreSQL"**
2. Name: `pontus-db`
3. Database: `routing_db`
4. User: `pontus_user` (or auto-generated)
5. Region: Oregon (US West) - same as web service
6. Plan: Free (for testing) or Starter ($7/month) for production
7. Click **"Create Database"**
8. Copy the **Internal Database URL** (use this for `DATABASE_URL`)

### 2. Create Redis Instance (Required)

1. In Render dashboard, click **"New +"** → **"Redis"**
2. Name: `pontus-redis`
3. Region: Oregon (US West) - same as web service
4. Plan: Free (for testing) or Starter ($7/month) for production
5. Click **"Create Redis"**
6. Copy the **Internal Redis URL** (use this for `REDIS_URL`)

### 3. Create Web Service

1. **Source Code:**
   - Repository: `4rjunD/PontusExecution`
   - Branch: `main`

2. **Settings:**
   - **Root Directory:** `Pontus-Execution-Layer` ⚠️ **CRITICAL**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Environment Variables:**
   - Add `DATABASE_URL` from step 1
   - Add `REDIS_URL` from step 2
   - Add `EXECUTION_MODE=simulation`
   - Add any optional API keys you have

4. **Instance Type:**
   - Starter ($7/month) for testing
   - Standard ($25/month) for production

5. Click **"Create Web Service"**

### 4. Verify Deployment

Once deployed, your service will be available at:
- **URL:** `https://pontusexecution.onrender.com` (or your custom domain)
- **Health Check:** `https://pontusexecution.onrender.com/health`
- **API Docs:** `https://pontusexecution.onrender.com/docs`

## Important Notes

### Root Directory
⚠️ **CRITICAL:** You MUST set the Root Directory to `Pontus-Execution-Layer` because:
- Your `requirements.txt` and `app/` directory are in that folder
- Without it, Render will look for files in the repository root and fail

### Database Connection
- Use the **Internal Database URL** from Render (not external)
- Format: `postgresql+asyncpg://user:password@host:port/dbname`
- Render automatically handles connection pooling

### Redis Connection
- Use the **Internal Redis URL** from Render
- Format: `redis://host:port/0`
- Internal URLs allow services in the same region to communicate privately

### Port Configuration
- Render sets `$PORT` automatically
- Do NOT hardcode port 8000
- Use `--port $PORT` in the start command

### Health Checks
- Render will automatically check `/health` endpoint
- Your app has a health endpoint at `/health` (verify in `app/main.py`)

## Troubleshooting

### Build Fails
- Check Root Directory is set to `Pontus-Execution-Layer`
- Verify `requirements.txt` exists in that directory
- Check build logs for specific error messages

### Application Won't Start
- Verify Start Command uses `$PORT` not hardcoded port
- Check environment variables are set correctly
- Verify DATABASE_URL and REDIS_URL are correct
- Check application logs in Render dashboard

### Database Connection Errors
- Ensure PostgreSQL service is running
- Use Internal Database URL (not external)
- Verify database credentials are correct

### Redis Connection Errors
- Ensure Redis service is running
- Use Internal Redis URL
- Check Redis service is in same region

## Production Recommendations

1. **Enable API Key Authentication:**
   ```bash
   REQUIRE_API_KEY=true
   API_KEYS=your-secret-api-key-1,your-secret-api-key-2
   ```

2. **Set CORS Origins:**
   ```bash
   CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   ```

3. **Use Standard Instance:**
   - 2 GB RAM recommended for production workloads
   - Better performance for routing calculations

4. **Set Up Custom Domain:**
   - Add your domain in Render dashboard
   - Configure DNS records as instructed

5. **Enable Auto-Deploy:**
   - Auto-deploy from main branch
   - Manual deploys for other branches

## Quick Reference

```
Repository: 4rjunD/PontusExecution
Branch: main
Root Directory: Pontus-Execution-Layer
Build: pip install -r requirements.txt
Start: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

