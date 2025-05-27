#!/bin/bash
# Check MCP SPARQL Server service status

echo "=== MCP SPARQL Server Status ==="
echo

# Check if we're in a systemd environment
if command -v systemctl &> /dev/null && [ -f /etc/systemd/system/mcp-sparql-http.service ]; then
    echo "📋 Available Services:"
    echo "  - mcp-sparql.service      (stdio transport)"
    echo "  - mcp-sparql-http.service (HTTP transport)"
    echo

    echo "🔍 Service Status:"
    for service in mcp-sparql mcp-sparql-http; do
        if sudo systemctl is-active --quiet $service; then
            status="✅ RUNNING"
        else
            status="❌ STOPPED"
        fi
        echo "  $service: $status"
    done

    echo

    if sudo systemctl is-active --quiet mcp-sparql-http; then
        echo "🌐 HTTP Service Details:"
        sudo systemctl status mcp-sparql-http --no-pager -l | head -10
        echo
        echo "📍 MCP Endpoint: http://localhost:8000/mcp/"
    fi

    echo "📊 Quick Commands:"
    echo "  ./start.sh [stdio|http]  - Start service"
    echo "  ./stop.sh [stdio|http]   - Stop service"
    echo "  ./logs.sh [stdio|http]   - View logs"
    echo "  sudo systemctl restart mcp-sparql-http"
else
    echo "📋 Local Development Mode"
    echo

    # Check for running processes
    if pgrep -f "python.*server.py" > /dev/null; then
        echo "🔍 Process Status:"
        echo "  MCP Server: ✅ RUNNING"
        echo
        echo "📍 Running processes:"
        ps aux | grep "python.*server.py" | grep -v grep
    else
        echo "🔍 Process Status:"
        echo "  MCP Server: ❌ STOPPED"
    fi

    echo
    echo "📊 Quick Commands:"
    echo "  ./start.sh [stdio|http]  - Start server"
    echo "  ./stop.sh                - Stop server"
    echo "  export SPARQL_ENDPOINT=https://your-endpoint.com/sparql"
fi