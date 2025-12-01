#!/bin/bash

# Quick start script for Route Intelligence Layer

echo "Starting Route Intelligence Layer..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Start services
echo "Starting PostgreSQL and Redis..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 5

# Check if services are up
if ! docker-compose ps | grep -q "Up"; then
    echo "Error: Services failed to start. Check docker-compose logs."
    exit 1
fi

# Run the application
echo "Starting FastAPI application..."
python -m app.main

