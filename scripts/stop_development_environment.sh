#!/bin/bash
echo "🛑 Stopping CMZ Development Environment..."

# Kill saved PIDs
if [ -f ".backend.pid" ]; then
    kill $(cat .backend.pid) 2>/dev/null || true
    rm .backend.pid
fi

if [ -f ".frontend.pid" ]; then
    kill $(cat .frontend.pid) 2>/dev/null || true
    rm .frontend.pid
fi

# Kill by port
lsof -ti:3000,3001,8080 | xargs kill -9 2>/dev/null || true

# Stop Docker containers
make stop-api 2>/dev/null || true

echo "✅ Development environment stopped"