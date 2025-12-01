#!/bin/bash
# Complete System Setup Script
# Sets up PostgreSQL, Redis, and populates route data

set -e

echo "=========================================="
echo "🚀 PONTUS EXECUTION LAYER - COMPLETE SETUP"
echo "=========================================="
echo ""

cd "$(dirname "$0")"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✅ Docker found${NC}"
    USE_DOCKER=true
elif command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}✅ Docker Compose found${NC}"
    USE_DOCKER=true
else
    echo -e "${YELLOW}⚠️  Docker not found, will try Homebrew setup${NC}"
    USE_DOCKER=false
fi

# Setup PostgreSQL
echo ""
echo "=========================================="
echo "Setting up PostgreSQL..."
echo "=========================================="

if [ "$USE_DOCKER" = true ]; then
    echo "Using Docker Compose..."
    docker compose up -d postgres
    echo "Waiting for PostgreSQL to be ready..."
    sleep 5
else
    echo "Checking for PostgreSQL via Homebrew..."
    if command -v psql &> /dev/null; then
        echo "PostgreSQL found, starting service..."
        brew services start postgresql@15 2>/dev/null || brew services start postgresql 2>/dev/null || echo "Please start PostgreSQL manually"
    else
        echo -e "${YELLOW}PostgreSQL not found. Please install:${NC}"
        echo "  brew install postgresql@15"
        echo "  brew services start postgresql@15"
        echo "  createdb routing_db"
    fi
fi

# Setup Redis
echo ""
echo "=========================================="
echo "Setting up Redis..."
echo "=========================================="

if [ "$USE_DOCKER" = true ]; then
    echo "Using Docker Compose..."
    docker compose up -d redis
    echo "Waiting for Redis to be ready..."
    sleep 3
else
    echo "Checking for Redis via Homebrew..."
    if command -v redis-cli &> /dev/null; then
        echo "Redis found, starting service..."
        brew services start redis 2>/dev/null || echo "Please start Redis manually"
    else
        echo -e "${YELLOW}Redis not found. Please install:${NC}"
        echo "  brew install redis"
        echo "  brew services start redis"
    fi
fi

# Wait a bit for services to be ready
echo ""
echo "Waiting for services to be ready..."
sleep 3

# Setup database schema and populate data
echo ""
echo "=========================================="
echo "Setting up database schema and data..."
echo "=========================================="

python3 setup_database.py

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}=========================================="
    echo "✅ SETUP COMPLETE!"
    echo "==========================================${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Start the server:"
    echo "     python -m app.main"
    echo ""
    echo "  2. Test the API:"
    echo "     curl http://localhost:8000/api/routes/optimize?from_asset=USD&to_asset=EUR&amount=1000"
    echo ""
    echo "  3. View API docs:"
    echo "     http://localhost:8000/docs"
    echo ""
else
    echo ""
    echo -e "${RED}=========================================="
    echo "❌ SETUP FAILED"
    echo "==========================================${NC}"
    echo ""
    echo "Please check the errors above and:"
    echo "  1. Ensure PostgreSQL is running"
    echo "  2. Ensure Redis is running"
    echo "  3. Check .env file configuration"
    echo ""
    exit 1
fi

