#!/bin/bash
set -e

echo "🚀 Starting CMZ Development Environment..."

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -i:$port >/dev/null 2>&1; then
        echo "⚠️  Port $port is in use"
        lsof -i:$port
        read -p "Kill existing process? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            lsof -ti:$port | xargs kill -9 2>/dev/null || true
            sleep 2
        else
            echo "❌ Cannot start services with port conflict"
            exit 1
        fi
    fi
}

# Function to wait for service health
wait_for_health() {
    local url=$1
    local service=$2
    local max_attempts=30
    local attempt=1

    echo "⏳ Waiting for $service to be healthy..."
    while [ $attempt -le $max_attempts ]; do
        if curl -f "$url" >/dev/null 2>&1; then
            echo "✅ $service is healthy"
            return 0
        fi
        echo "   Attempt $attempt/$max_attempts: $service not ready..."
        sleep 2
        ((attempt++))
    done

    echo "❌ $service failed to start within timeout"
    return 1
}

# Check and kill conflicting ports
check_port 3000
check_port 3001
check_port 8080

# Verify AWS credentials
if ! aws sts get-caller-identity --profile cmz >/dev/null 2>&1; then
    echo "❌ AWS credentials not configured for CMZ profile"
    echo "Run: aws configure --profile cmz"
    exit 1
fi

# Start backend API
echo "🔧 Starting backend API..."
cd "$(dirname "$0")/.."
make generate-api && make build-api && make run-api &
BACKEND_PID=$!

# Wait for backend health
if wait_for_health "http://localhost:8080/health" "Backend API"; then
    echo "✅ Backend API started successfully (PID: $BACKEND_PID)"
else
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# Start frontend (detect which port to use)
echo "🎨 Starting frontend..."
cd frontend
if [ -f "package.json" ]; then
    npm run dev &
    FRONTEND_PID=$!

    # Try both common ports
    if wait_for_health "http://localhost:3000" "Frontend (port 3000)"; then
        FRONTEND_URL="http://localhost:3000"
    elif wait_for_health "http://localhost:3001" "Frontend (port 3001)"; then
        FRONTEND_URL="http://localhost:3001"
    else
        echo "❌ Frontend failed to start"
        kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
        exit 1
    fi

    echo "✅ Frontend started successfully at $FRONTEND_URL (PID: $FRONTEND_PID)"
else
    echo "⚠️  No frontend package.json found, skipping frontend startup"
fi

# Verify full system health
echo "🔍 Running system health check..."
if curl -f http://localhost:8080/health >/dev/null 2>&1; then
    echo "✅ Backend API: HEALTHY"
else
    echo "❌ Backend API: UNHEALTHY"
fi

if [ -n "$FRONTEND_URL" ] && curl -f "$FRONTEND_URL" >/dev/null 2>&1; then
    echo "✅ Frontend: HEALTHY"
else
    echo "❌ Frontend: UNHEALTHY"
fi

# Verify database connectivity
if aws dynamodb list-tables --region us-west-2 --profile cmz >/dev/null 2>&1; then
    echo "✅ DynamoDB: CONNECTED"
else
    echo "❌ DynamoDB: CONNECTION FAILED"
fi

echo "🎉 Development environment startup complete!"
echo "   Backend API: http://localhost:8080"
echo "   Frontend: $FRONTEND_URL"
echo "   Logs: make logs-api"

# Save PIDs for cleanup
echo "$BACKEND_PID" > .backend.pid
[ -n "$FRONTEND_PID" ] && echo "$FRONTEND_PID" > .frontend.pid