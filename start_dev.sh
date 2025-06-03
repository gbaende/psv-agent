#!/bin/bash

# DealTracker Sales Agent - Development Startup Script

echo "🚀 Starting DealTracker Sales Agent..."

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  No .env file found. Please copy backend/.env.example to backend/.env and configure your settings."
    exit 1
fi

# Function to start backend
start_backend() {
    echo "📡 Starting Backend API..."
    cd backend
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    echo "Backend started with PID: $BACKEND_PID"
}

# Function to start frontend
start_frontend() {
    echo "🎨 Starting Frontend..."
    cd frontend
    npm start &
    FRONTEND_PID=$!
    cd ..
    echo "Frontend started with PID: $FRONTEND_PID"
}

# Function to cleanup on exit
cleanup() {
    echo "🛑 Shutting down services..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start services
start_backend
sleep 3
start_frontend

echo ""
echo "✅ DealTracker Sales Agent is running!"
echo "📡 Backend API: http://localhost:8000"
echo "🎨 Frontend: http://localhost:3000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for services
wait 