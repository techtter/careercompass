# CareerCompassAI Server Startup Guide

This guide explains how to start the CareerCompassAI servers properly.

## Quick Start

### Option 1: Start Both Servers (Recommended)
```bash
./start_servers.sh
```
This will start both backend (port 8000) and frontend (port 3000) servers automatically.

### Option 2: Start Servers Individually

#### Backend Only
```bash
python start_backend.py
```
This starts the FastAPI backend server on http://127.0.0.1:8000

#### Frontend Only
```bash
python start_frontend.py
```
This starts the Next.js frontend server on http://localhost:3000

## Manual Startup (Alternative)

If you prefer to start servers manually:

### Backend
```bash
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend
```bash
cd frontend
npm run dev
```

## Troubleshooting

### Port Already in Use Error
If you get "Address already in use" errors, run:
```bash
pkill -f "uvicorn|npm|next"
lsof -ti:8000,3000 | xargs kill -9
```

### Module Import Errors
The startup scripts automatically handle directory changes to ensure modules are imported correctly. If you're getting import errors when starting manually, make sure you're in the correct directory:
- For backend: Must be in the `backend/` directory
- For frontend: Must be in the `frontend/` directory

## Server URLs

- **Backend API**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs
- **Frontend**: http://localhost:3000

## Stopping Servers

- Press `Ctrl+C` in the terminal where servers are running
- Or use: `pkill -f "uvicorn|npm|next"`

## Files Created

- `start_backend.py` - Python script to start backend server
- `start_frontend.py` - Python script to start frontend server  
- `start_servers.sh` - Bash script to start both servers
- `SERVER_STARTUP.md` - This documentation file 