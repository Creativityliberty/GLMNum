#!/bin/bash
"""
Cleanup Script - Kill all processes and reset ports
====================================================

Kills all Python/uvicorn processes and resets the system.
"""

echo "🧹 Cleaning up all processes..."
echo ""

# Kill all Python processes
echo "❌ Killing Python processes..."
pkill -f "python" 2>/dev/null
pkill -f "uvicorn" 2>/dev/null
pkill -f "api" 2>/dev/null
sleep 1

# Kill processes on specific ports
echo "❌ Killing processes on ports 8000-8090..."
for port in {8000..8090}; do
    lsof -ti:$port | xargs kill -9 2>/dev/null
done
sleep 1

# Verify cleanup
echo ""
echo "✅ Cleanup complete!"
echo ""
echo "🔍 Checking for remaining processes..."
ps aux | grep -E "python|uvicorn|api" | grep -v grep || echo "✅ No processes found"

echo ""
echo "🔍 Checking ports..."
for port in 8000 8080 8081; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  Port $port is still in use"
    else
        echo "✅ Port $port is free"
    fi
done

echo ""
echo "✅ System reset complete!"
echo ""
echo "Ready to start fresh. Run:"
echo "  python backend.py"
echo "or"
echo "  uvicorn backend:app --host 0.0.0.0 --port 8081"
