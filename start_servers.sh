#!/bin/bash

# CareerCompassAI Server Startup Script
# This script starts both backend and frontend servers

echo "🚀 Starting CareerCompassAI Servers"
echo "=================================="

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f "uvicorn|npm|next" 2>/dev/null || true
lsof -ti:8000,3000 | xargs kill -9 2>/dev/null || true

sleep 2

# Start backend server in background
echo "🔧 Starting backend server on port 8000..."
python start_backend.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Check if backend is running
if curl -s http://127.0.0.1:8000/docs > /dev/null; then
    echo "✅ Backend server started successfully on http://127.0.0.1:8000"
else
    echo "❌ Backend server failed to start"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# Start frontend server
echo "🎨 Starting frontend server on port 3000..."
python start_frontend.py &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 5

# Check if frontend is running
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend server started successfully on http://localhost:3000"
else
    echo "❌ Frontend server failed to start"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 1
fi

echo ""
echo "🎉 Both servers are running!"
echo "📊 Backend API: http://127.0.0.1:8000"
echo "🌐 Frontend:    http://localhost:3000"
echo "📚 API Docs:    http://127.0.0.1:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user interrupt
trap 'echo ""; echo "🛑 Stopping servers..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; exit 0' INT

# Keep script running
wait 