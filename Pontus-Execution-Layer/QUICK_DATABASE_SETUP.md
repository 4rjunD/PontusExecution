# Quick Database Setup Guide

## Option 1: Docker (Recommended - Easiest)

```bash
cd /Users/arjundixit/Downloads/PontusExecution/Pontus-Execution-Layer
docker compose up -d
python3 setup_database.py
```

## Option 2: Homebrew (macOS)

### Install PostgreSQL
```bash
brew install postgresql@15
brew services start postgresql@15
createdb routing_db
```

### Install Redis
```bash
brew install redis
brew services start redis
```

### Run Setup
```bash
python3 setup_database.py
```

## Option 3: Cloud Services (Free Tiers)

### PostgreSQL
- **Supabase**: https://supabase.com (Free tier)
- **Neon**: https://neon.tech (Free tier)

### Redis
- **Upstash**: https://upstash.com (Free tier)

### Update .env
```bash
DATABASE_URL=postgresql+asyncpg://user:password@host:port/dbname
REDIS_URL=redis://user:password@host:port
```

## Option 4: Skip Database (Limited Functionality)

The system can run without databases for testing API features, but:
- Routes won't be calculated
- Execution won't work with real routes
- Background tasks won't populate data

