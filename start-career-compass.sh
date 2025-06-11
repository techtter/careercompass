#!/bin/bash

echo "🚀 Starting Career Compass AI Development Server"
echo "=============================================="

# Navigate to frontend directory
cd frontend

# Kill any process running on port 3000
echo "🔄 Killing any existing processes on port 3000..."
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

# Wait a moment for processes to fully terminate
sleep 2

# Clear cache and temporary files
echo "🧹 Clearing cache..."
rm -rf .next node_modules/.cache 2>/dev/null || true

# Ensure dependencies are installed
echo "📦 Checking dependencies..."
npm install --silent

# Verify Tailwind CSS is properly configured
echo "🎨 Verifying Tailwind CSS configuration..."
if [ ! -f "tailwind.config.js" ]; then
    echo "❌ Tailwind config missing!"
    exit 1
fi

# Start the development server
echo "🚀 Starting server on http://localhost:3000..."
echo "💡 UI should now display properly with fonts and styles"
echo "🔗 Access: http://localhost:3000"
echo "Press Ctrl+C to stop the server"
echo "=============================================="

npm run dev 