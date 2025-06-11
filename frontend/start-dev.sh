#!/bin/bash

# Kill any process running on port 3000
echo "🔄 Killing any processes on port 3000..."
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

# Wait a moment for processes to fully terminate
sleep 1

# Start the development server
echo "🚀 Starting Career Compass AI on port 3000..."
npm run dev 