# Render Environment Variables Setup Guide

## ⚠️ Current Issue

Your environment variables are set to placeholder values like `'from-render-redis-service'` instead of actual service URLs. You need to:

1. **Create Redis and PostgreSQL services in Render**
2. **Copy the actual connection URLs**
3. **Update your environment variables**

## Step-by-Step Setup

### 1. Create PostgreSQL Database

1. In Render dashboard, click **"New +"** → **"PostgreSQL"**
2. Configure:
   - **Name:** `pontus-db` (or any name)
   - **Database:** `routing_db`
   - **User:** (auto-generated or choose)
   - **Region:** Oregon (US West) - **same region as your web service**
   - **Plan:** Free (for testing) or Starter ($7/month)
3. Click **"Create Database"**
4. **IMPORTANT:** After creation, go to the database service
5. Find **"Internal Database URL"** (not External)
6. Copy the full URL - it looks like:
   ```
   postgresql://user:password@hostname:5432/routing_db
   ```
7. Convert it to asyncpg format:
   ```
   postgresql+asyncpg://user:password@hostname:5432/routing_db
   ```
   (Just add `+asyncpg` after `postgresql`)

### 2. Create Redis Instance

1. In Render dashboard, click **"New +"** → **"Redis"**
2. Configure:
   - **Name:** `pontus-redis` (or any name)
   - **Region:** Oregon (US West) - **same region as your web service**
   - **Plan:** Free (for testing) or Starter ($7/month)
3. Click **"Create Redis"**
4. **IMPORTANT:** After creation, go to the Redis service
5. Find **"Internal Redis URL"** (not External)
6. Copy the full URL - it looks like:
   ```
   redis://hostname:6379
   ```
   or
   ```
   redis://:password@hostname:6379
   ```

### 3. Update Environment Variables in Your Web Service

1. Go to your **Web Service** settings
2. Click **"Environment"** tab
3. Update these variables:

#### Required Variables:

**DATABASE_URL:**
- Key: `DATABASE_URL`
- Value: The PostgreSQL URL you copied, with `+asyncpg` added:
  ```
  postgresql+asyncpg://user:password@hostname:5432/routing_db
  ```

**REDIS_URL:**
- Key: `REDIS_URL`
- Value: The Redis URL you copied:
  ```
  redis://hostname:6379
  ```
  or if it has a password:
  ```
  redis://:password@hostname:6379
  ```

**EXECUTION_MODE:**
- Key: `EXECUTION_MODE`
- Value: `simulation`

#### Optional Variables (add if needed):

```bash
CORS_ORIGINS=*
REQUIRE_API_KEY=false
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

### 4. Save and Redeploy

1. Click **"Save Changes"**
2. Render will automatically trigger a new deploy
3. Wait for the deployment to complete
4. Check the logs - Redis errors should be gone!

## Important Notes

### Internal vs External URLs

- **Always use Internal URLs** for services in the same region
- Internal URLs allow services to communicate over Render's private network
- External URLs are for connecting from outside Render

### Region Matching

- **All services must be in the same region** (Oregon in your case)
- Services in different regions cannot use Internal URLs

### URL Format

**PostgreSQL:**
- Render gives you: `postgresql://...`
- You need: `postgresql+asyncpg://...` (add `+asyncpg`)
- This tells SQLAlchemy to use the asyncpg driver

**Redis:**
- Render gives you: `redis://...`
- Use it as-is (no changes needed)

## Troubleshooting

### Still seeing Redis errors?

1. **Check the URL format:**
   - Should start with `redis://`
   - Should include hostname and port
   - Example: `redis://d-redis-xxxxx.render.com:6379`

2. **Verify services are running:**
   - Go to your Redis service dashboard
   - Check it shows "Running" status
   - Same for PostgreSQL

3. **Check region:**
   - All services must be in the same region
   - Web service, Redis, and PostgreSQL should all be in Oregon

4. **Wait for services to be ready:**
   - New services take 1-2 minutes to fully start
   - Check service status before using URLs

### Database connection errors?

1. **Check DATABASE_URL format:**
   - Must include `+asyncpg`: `postgresql+asyncpg://...`
   - Must include database name at the end

2. **Verify credentials:**
   - Check username and password in the URL
   - Make sure database name matches (`routing_db`)

## Quick Checklist

- [ ] PostgreSQL service created
- [ ] Redis service created
- [ ] Both services in same region (Oregon)
- [ ] DATABASE_URL updated with Internal URL + `+asyncpg`
- [ ] REDIS_URL updated with Internal URL
- [ ] EXECUTION_MODE set to `simulation`
- [ ] Environment variables saved
- [ ] Service redeployed
- [ ] No more Redis errors in logs!

