#!/bin/bash
# Restart MCP Luxembourg Legal Server

set -e

echo "🔄 Restarting MCP Luxembourg Legal Server..."

# Stop the server first
echo "⏹️  Stopping server..."
./stop.sh

# Wait a moment for clean shutdown
sleep 2

# Start the server
echo "🚀 Starting server..."
./start.sh "$@"