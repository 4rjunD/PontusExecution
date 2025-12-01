# Database Setup Guide

## Current Status
- ✅ PostgreSQL: Not installed
- ✅ Redis: Not installed
- ✅ Docker: Not available

## Option 1: Install via Homebrew (Recommended for macOS)

### Install PostgreSQL
```bash
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb routing_db

# Or manually:
psql postgres
CREATE DATABASE routing_db;
\q
```

### Install Redis
```bash
brew install redis
brew services start redis
```

### Verify Installation
```bash
# Check PostgreSQL
psql -d routing_db -c "SELECT version();"

# Check Redis
redis-cli ping
# Should return: PONG
```

## Option 2: Use Docker (if available)

```bash
cd /Users/arjundixit/Downloads/PontusExecution/Pontus-Execution-Layer
docker compose up -d
```

## Option 3: Use Cloud Services (Free Tiers)

### PostgreSQL
- **Supabase**: https://supabase.com (Free tier)
- **Neon**: https://neon.tech (Free tier)
- **Railway**: https://railway.app (Free tier)

### Redis
- **Upstash**: https://upstash.com (Free tier)
- **Redis Cloud**: https://redis.com/try-free/ (Free tier)

### Update .env
```bash
# For cloud services, update DATABASE_URL and REDIS_URL in .env
DATABASE_URL=postgresql+asyncpg://user:password@host:port/dbname
REDIS_URL=redis://user:password@host:port
```

## Option 4: Run Without Databases (Limited Functionality)

The system can run without databases, but:
- ❌ No data persistence
- ❌ No caching
- ❌ Background tasks won't populate data
- ✅ API endpoints will work with in-memory data
- ✅ Execution layer will work in simulation mode

## After Setup

1. **Update .env file** with database credentials
2. **Restart the server**:
   ```bash
   # Kill existing server
   lsof -ti:8000 | xargs kill -9
   
   # Start server
   cd /Users/arjundixit/Downloads/PontusExecution/Pontus-Execution-Layer
   python -m app.main
   ```

3. **Verify connection**:
   ```bash
   curl http://localhost:8000/api/health
   ```

4. **Check background tasks** are populating data:
   ```bash
   curl http://localhost:8000/api/routes/segments?limit=5
   ```

