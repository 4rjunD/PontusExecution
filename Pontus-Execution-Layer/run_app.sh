#!/bin/bash
# Run the Route Intelligence Layer application

echo "Starting Route Intelligence Layer..."
echo ""

# Check if dependencies are installed
echo "Checking dependencies..."
python3 -c "import fastapi, httpx, sqlalchemy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip3 install -q -r requirements.txt
fi

# Check for Docker (optional - for Postgres/Redis)
if command -v docker &> /dev/null; then
    echo "Starting Docker services..."
    docker compose up -d 2>/dev/null || docker-compose up -d 2>/dev/null
    sleep 3
else
    echo "⚠️  Docker not found. App will run but may need Postgres/Redis running separately."
    echo "   You can install Docker or run Postgres/Redis manually."
    echo ""
fi

# Run the application
echo "Starting FastAPI application..."
echo "Access the API at: http://localhost:8000"
echo "API docs at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 -m app.main

