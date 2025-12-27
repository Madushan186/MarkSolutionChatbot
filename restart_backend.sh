#!/bin/bash

echo "🛑 Stopping current backend..."
pkill -f "uvicorn main:app"

echo "⏳ Waiting for port 8000 to clear..."
sleep 2

echo "🚀 Starting backend..."
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
