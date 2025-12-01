#!/bin/bash
# Production Infrastructure Deployment Script
# Sets up PostgreSQL, Redis, and initializes the database

set -e  # Exit on error

echo "=================================================================================="
echo "🚀 PRODUCTION INFRASTRUCTURE DEPLOYMENT"
echo "=================================================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is available
check_docker() {
    if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
        if docker info &> /dev/null; then
            return 0
        fi
    fi
    return 1
}

# Check if PostgreSQL is running locally
check_postgres_local() {
    if command -v psql &> /dev/null; then
        if psql -h localhost -U postgres -d postgres -c "SELECT 1" &> /dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

# Check if Redis is running locally
check_redis_local() {
    if command -v redis-cli &> /dev/null; then
        if redis-cli ping &> /dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

# Setup PostgreSQL with Docker
setup_postgres_docker() {
    echo "Step 1: Setting up PostgreSQL with Docker..."
    
    if ! check_docker; then
        print_error "Docker is not available. Please install Docker or set up PostgreSQL manually."
        return 1
    fi
    
    # Start PostgreSQL container
    echo "  Starting PostgreSQL container..."
    docker-compose up -d postgres
    
    # Wait for PostgreSQL to be ready
    echo "  Waiting for PostgreSQL to be ready..."
    max_attempts=30
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose exec -T postgres pg_isready -U postgres &> /dev/null; then
            print_status "PostgreSQL is ready"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    
    print_error "PostgreSQL failed to start within 30 seconds"
    return 1
}

# Setup Redis with Docker
setup_redis_docker() {
    echo "Step 2: Setting up Redis with Docker..."
    
    if ! check_docker; then
        print_error "Docker is not available. Please install Docker or set up Redis manually."
        return 1
    fi
    
    # Start Redis container
    echo "  Starting Redis container..."
    docker-compose up -d redis
    
    # Wait for Redis to be ready
    echo "  Waiting for Redis to be ready..."
    max_attempts=30
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose exec -T redis redis-cli ping &> /dev/null; then
            print_status "Redis is ready"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    
    print_error "Redis failed to start within 30 seconds"
    return 1
}

# Setup PostgreSQL locally (Homebrew)
setup_postgres_local() {
    echo "Step 1: Setting up PostgreSQL locally..."
    
    if ! command -v psql &> /dev/null; then
        print_warning "PostgreSQL not found. Installing via Homebrew..."
        if command -v brew &> /dev/null; then
            brew install postgresql@15
            brew services start postgresql@15
        else
            print_error "Homebrew not found. Please install PostgreSQL manually."
            return 1
        fi
    fi
    
    # Create database if it doesn't exist
    echo "  Creating database 'routing_db'..."
    createdb routing_db 2>/dev/null || print_warning "Database may already exist"
    
    print_status "PostgreSQL is ready"
    return 0
}

# Setup Redis locally (Homebrew)
setup_redis_local() {
    echo "Step 2: Setting up Redis locally..."
    
    if ! command -v redis-cli &> /dev/null; then
        print_warning "Redis not found. Installing via Homebrew..."
        if command -v brew &> /dev/null; then
            brew install redis
            brew services start redis
        else
            print_error "Homebrew not found. Please install Redis manually."
            return 1
        fi
    else
        # Start Redis if not running
        if ! redis-cli ping &> /dev/null 2>&1; then
            print_warning "Redis not running. Starting Redis..."
            if command -v brew &> /dev/null; then
                brew services start redis
            fi
        fi
    fi
    
    # Wait for Redis to be ready
    max_attempts=10
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if redis-cli ping &> /dev/null 2>&1; then
            print_status "Redis is ready"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    
    print_error "Redis failed to start"
    return 1
}

# Initialize database schema
init_database() {
    echo ""
    echo "Step 3: Initializing database schema..."
    
    cd "$(dirname "$0")"
    python3 setup_database.py
    
    if [ $? -eq 0 ]; then
        print_status "Database initialized successfully"
        return 0
    else
        print_error "Database initialization failed"
        return 1
    fi
}

# Test Redis connection
test_redis() {
    echo ""
    echo "Step 4: Testing Redis connection..."
    
    cd "$(dirname "$0")"
    python3 setup_redis.py
    
    if [ $? -eq 0 ]; then
        print_status "Redis connection verified"
        return 0
    else
        print_error "Redis connection failed"
        return 1
    fi
}

# Main deployment function
main() {
    echo "Checking infrastructure requirements..."
    echo ""
    
    USE_DOCKER=false
    if check_docker; then
        echo "Docker detected. Using Docker for deployment."
        USE_DOCKER=true
    else
        echo "Docker not available. Using local installation."
    fi
    echo ""
    
    # Setup PostgreSQL
    if [ "$USE_DOCKER" = true ]; then
        setup_postgres_docker || exit 1
    else
        setup_postgres_local || exit 1
    fi
    
    # Setup Redis
    if [ "$USE_DOCKER" = true ]; then
        setup_redis_docker || exit 1
    else
        setup_redis_local || exit 1
    fi
    
    # Initialize database
    init_database || exit 1
    
    # Test Redis
    test_redis || exit 1
    
    echo ""
    echo "=================================================================================="
    echo "🎉 PRODUCTION INFRASTRUCTURE DEPLOYMENT COMPLETE!"
    echo "=================================================================================="
    echo ""
    echo "✅ PostgreSQL: Running and initialized"
    echo "✅ Redis: Running and tested"
    echo "✅ Database: Schema created and populated"
    echo ""
    echo "Next steps:"
    echo "  1. Start the server: python -m app.main"
    echo "  2. Or use uvicorn: uvicorn app.main:app --reload"
    echo "  3. Test API: curl http://localhost:8000/health"
    echo ""
    echo "To stop services (if using Docker):"
    echo "  docker-compose down"
    echo ""
    echo "To stop services (if using local):"
    echo "  brew services stop postgresql@15"
    echo "  brew services stop redis"
    echo ""
}

# Run main function
main

