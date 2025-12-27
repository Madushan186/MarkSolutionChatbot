#!/bin/bash
echo "Stopping all processes..."
pkill -f "uvicorn"
pkill -f "node"
pkill -f "ollama"
echo "✅ All servers stopped."
