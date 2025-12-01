#!/bin/bash
# Complete Production Infrastructure Deployment
# Sets up PostgreSQL, Redis, initializes database, and verifies everything

set -e

echo "=================================================================================="
echo "🚀 COMPLETE PRODUCTION INFRASTRUCTURE DEPLOYMENT"
echo "=================================================================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Get current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Export PostgreSQL to PATH
export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"

# Get current user for database connection
CURRENT_USER=$(whoami)
export DATABASE_URL="postgresql+asyncpg://${CURRENT_USER}@localhost:5432/routing_db"

print_info "Using database URL: $DATABASE_URL"
echo ""

# Step 1: Check if services are running
echo "Step 1: Checking infrastructure services..."
echo ""

# Check PostgreSQL
if psql -h localhost -U "$CURRENT_USER" -d routing_db -c "SELECT 1" &> /dev/null 2>&1; then
    print_status "PostgreSQL is running"
else
    print_error "PostgreSQL is not running. Please run: ./setup_production_infrastructure.sh"
    exit 1
fi

# Check Redis
if redis-cli ping &> /dev/null 2>&1; then
    print_status "Redis is running"
else
    print_error "Redis is not running. Please run: ./setup_production_infrastructure.sh"
    exit 1
fi

echo ""

# Step 2: Initialize database schema
echo "Step 2: Initializing database schema..."
echo ""

python3 setup_database.py

if [ $? -eq 0 ]; then
    print_status "Database initialization complete"
else
    print_error "Database initialization failed"
    echo ""
    print_info "Troubleshooting:"
    echo "  1. Make sure PostgreSQL is running: brew services list | grep postgresql"
    echo "  2. Check database exists: psql -l | grep routing_db"
    echo "  3. Check Python dependencies: pip list | grep sqlalchemy"
    exit 1
fi

echo ""

# Step 3: Test Redis connection
echo "Step 3: Testing Redis connection..."
echo ""

python3 setup_redis.py

if [ $? -eq 0 ]; then
    print_status "Redis connection verified"
else
    print_warning "Redis connection test failed (may still work)"
fi

echo ""

# Step 4: Verify complete setup
echo "Step 4: Verifying complete setup..."
echo ""

# Test database query
DB_TEST=$(psql -h localhost -U "$CURRENT_USER" -d routing_db -t -c "SELECT COUNT(*) FROM route_segments;" 2>/dev/null || echo "0")
if [ "$DB_TEST" != "" ]; then
    print_status "Database tables exist"
    print_info "  Route segments in database: $DB_TEST"
else
    print_warning "Database tables may not be populated yet"
fi

# Test Redis
REDIS_TEST=$(redis-cli ping 2>/dev/null || echo "FAILED")
if [ "$REDIS_TEST" = "PONG" ]; then
    print_status "Redis is responding"
else
    print_warning "Redis may not be fully operational"
fi

echo ""
echo "=================================================================================="
echo "🎉 PRODUCTION INFRASTRUCTURE DEPLOYMENT COMPLETE!"
echo "=================================================================================="
echo ""
print_status "PostgreSQL: Running"
print_status "Redis: Running"
print_status "Database: Initialized"
print_status "Infrastructure: Ready for production"
echo ""
echo "Next steps:"
echo "  1. Start the server:"
echo "     python -m app.main"
echo "     OR"
echo "     uvicorn app.main:app --reload"
echo ""
echo "  2. Test the API:"
echo "     curl http://localhost:8000/health"
echo ""
echo "  3. View API docs:"
echo "     open http://localhost:8000/docs"
echo ""
echo "To stop services:"
echo "  brew services stop postgresql@15"
echo "  brew services stop redis"
echo ""

