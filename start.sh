#!/bin/bash
# Start MCP SPARQL Server locally

set -e

if [ ! -f "venv/bin/activate" ]; then
    echo "❌ Virtual environment not found. Run ./install.sh first."
    exit 1
fi

source venv/bin/activate

if [ -z "$SPARQL_ENDPOINT" ]; then
    echo "⚠️  SPARQL_ENDPOINT not set. Using Luxembourg default endpoint."
    export SPARQL_ENDPOINT="https://data.legilux.public.lu/sparqlendpoint"
fi

if [ "$1" = "stdio" ]; then
    echo "🚀 Starting stdio server..."
    python server.py --endpoint "$SPARQL_ENDPOINT"
elif [ "$1" = "http" ]; then
    echo "🚀 Starting HTTP server (streamable-http transport)..."
    python server.py --transport streamable-http --host localhost --port 8000 --endpoint "$SPARQL_ENDPOINT"
else
    echo "🚀 Starting HTTP server (streamable-http transport - default)..."
    echo "🌐 Server will be available at: http://localhost:8000/mcp"
    echo "Use './start.sh stdio' for stdio mode"
    python server.py --transport streamable-http --host localhost --port 8000 --endpoint "$SPARQL_ENDPOINT"
fi