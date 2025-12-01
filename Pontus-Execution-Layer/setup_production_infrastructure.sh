#!/bin/bash
# Production Infrastructure Setup Script
# Installs and configures PostgreSQL and Redis for macOS

set -e

echo "=================================================================================="
echo "🚀 PRODUCTION INFRASTRUCTURE SETUP"
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

# Check for Homebrew
check_homebrew() {
    if ! command -v brew &> /dev/null; then
        print_error "Homebrew is not installed."
        echo ""
        echo "Please install Homebrew first:"
        echo '  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        echo ""
        exit 1
    fi
    print_status "Homebrew is installed"
}

# Install PostgreSQL
install_postgresql() {
    echo ""
    echo "Step 1: Installing PostgreSQL..."
    
    if command -v psql &> /dev/null; then
        print_info "PostgreSQL is already installed"
        psql --version
    else
        print_info "Installing PostgreSQL via Homebrew..."
        brew install postgresql@15
        
        # Add PostgreSQL to PATH
        if [ -f ~/.zshrc ]; then
            if ! grep -q "postgresql@15" ~/.zshrc; then
                echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
                export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
            fi
        elif [ -f ~/.bash_profile ]; then
            if ! grep -q "postgresql@15" ~/.bash_profile; then
                echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.bash_profile
                export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
            fi
        fi
        
        print_status "PostgreSQL installed"
    fi
}

# Start PostgreSQL service
start_postgresql() {
    echo ""
    echo "Step 2: Starting PostgreSQL service..."
    
    if brew services list | grep -q "postgresql@15.*started"; then
        print_info "PostgreSQL is already running"
    else
        print_info "Starting PostgreSQL service..."
        brew services start postgresql@15
        
        # Wait for PostgreSQL to be ready
        print_info "Waiting for PostgreSQL to be ready..."
        sleep 3
        
        max_attempts=10
        attempt=0
        while [ $attempt -lt $max_attempts ]; do
            if psql -h localhost -U $(whoami) -d postgres -c "SELECT 1" &> /dev/null 2>&1; then
                print_status "PostgreSQL is ready"
                return 0
            fi
            attempt=$((attempt + 1))
            sleep 1
        done
        
        print_warning "PostgreSQL may not be fully ready yet, but continuing..."
    fi
}

# Create database
create_database() {
    echo ""
    echo "Step 3: Creating database 'routing_db'..."
    
    # Try to create database
    if createdb routing_db 2>/dev/null; then
        print_status "Database 'routing_db' created"
    else
        # Check if database already exists
        if psql -h localhost -U $(whoami) -lqt | cut -d \| -f 1 | grep -qw routing_db; then
            print_info "Database 'routing_db' already exists"
        else
            print_error "Failed to create database"
            return 1
        fi
    fi
}

# Install Redis
install_redis() {
    echo ""
    echo "Step 4: Installing Redis..."
    
    if command -v redis-cli &> /dev/null; then
        print_info "Redis is already installed"
        redis-cli --version
    else
        print_info "Installing Redis via Homebrew..."
        brew install redis
        print_status "Redis installed"
    fi
}

# Start Redis service
start_redis() {
    echo ""
    echo "Step 5: Starting Redis service..."
    
    if brew services list | grep -q "redis.*started"; then
        print_info "Redis is already running"
    else
        print_info "Starting Redis service..."
        brew services start redis
        
        # Wait for Redis to be ready
        print_info "Waiting for Redis to be ready..."
        sleep 2
        
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
        
        print_warning "Redis may not be fully ready yet, but continuing..."
    fi
}

# Test connections
test_connections() {
    echo ""
    echo "Step 6: Testing connections..."
    
    # Test PostgreSQL
    if psql -h localhost -U $(whoami) -d routing_db -c "SELECT 1" &> /dev/null 2>&1; then
        print_status "PostgreSQL connection successful"
    else
        print_error "PostgreSQL connection failed"
        return 1
    fi
    
    # Test Redis
    if redis-cli ping &> /dev/null 2>&1; then
        print_status "Redis connection successful"
    else
        print_error "Redis connection failed"
        return 1
    fi
}

# Main setup
main() {
    check_homebrew
    install_postgresql
    start_postgresql
    create_database
    install_redis
    start_redis
    test_connections
    
    echo ""
    echo "=================================================================================="
    echo "🎉 INFRASTRUCTURE SETUP COMPLETE!"
    echo "=================================================================================="
    echo ""
    print_status "PostgreSQL: Installed and running"
    print_status "Redis: Installed and running"
    print_status "Database: routing_db created"
    echo ""
    echo "Next: Run the database initialization script:"
    echo "  python3 setup_database.py"
    echo ""
}

main

