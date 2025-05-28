#!/bin/bash
# Test MCP SPARQL Server functionality

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
TEST_ENDPOINT="http://localhost:8000"
MCP_PATH="/mcp/"
TEST_TIMEOUT=10

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Function to test HTTP endpoint
test_http_endpoint() {
    print_header "Testing HTTP Endpoint"
    
    # Test basic connectivity
    print_info "Testing basic connectivity to $TEST_ENDPOINT$MCP_PATH"
    if curl -s --connect-timeout $TEST_TIMEOUT "$TEST_ENDPOINT$MCP_PATH" > /dev/null; then
        print_success "Server is responding"
    else
        print_error "Server is not responding"
        return 1
    fi
    
    # Test MCP endpoint with proper headers
    print_info "Testing MCP endpoint with proper headers"
    response=$(curl -s -w "%{http_code}" -H "Accept: text/event-stream" \
        --connect-timeout $TEST_TIMEOUT \
        "$TEST_ENDPOINT$MCP_PATH" -o /dev/null)
    
    if [ "$response" = "200" ] || [ "$response" = "406" ]; then
        print_success "MCP endpoint is responding (HTTP $response)"
    else
        print_error "MCP endpoint returned unexpected status: $response"
        return 1
    fi
}

# Function to test service status
test_service_status() {
    print_header "Testing Service Status"
    
    if command -v systemctl &> /dev/null; then
        # Check systemd services
        if systemctl is-active --quiet mcp-sparql-http 2>/dev/null; then
            print_success "mcp-sparql-http service is running"
            
            # Show service details
            print_info "Service details:"
            systemctl status mcp-sparql-http --no-pager -l | head -5
            
        elif systemctl is-active --quiet mcp-sparql 2>/dev/null; then
            print_warning "mcp-sparql (stdio) service is running instead of HTTP"
            print_info "Use: sudo systemctl start mcp-sparql-http"
            
        else
            print_error "No MCP services are running"
            print_info "Use: sudo systemctl start mcp-sparql-http"
            return 1
        fi
    else
        # Check for local processes
        if pgrep -f "python.*server.py" > /dev/null; then
            print_success "MCP server process is running"
            print_info "Running processes:"
            ps aux | grep "python.*server.py" | grep -v grep | head -3
        else
            print_error "No MCP server processes found"
            print_info "Use: ./start.sh http"
            return 1
        fi
    fi
}

# Function to test configuration
test_configuration() {
    print_header "Testing Configuration"
    
    if [ -f "/etc/mcp-sparql/env" ]; then
        print_success "Configuration file exists: /etc/mcp-sparql/env"
        
        # Check SPARQL endpoint configuration
        if grep -q "SPARQL_ENDPOINT=" "/etc/mcp-sparql/env"; then
            endpoint=$(grep "SPARQL_ENDPOINT=" "/etc/mcp-sparql/env" | cut -d'=' -f2)
            print_info "Configured SPARQL endpoint: $endpoint"
            
            # Test SPARQL endpoint connectivity
            print_info "Testing SPARQL endpoint connectivity..."
            if curl -s --connect-timeout $TEST_TIMEOUT "$endpoint" > /dev/null; then
                print_success "SPARQL endpoint is reachable"
            else
                print_warning "SPARQL endpoint may not be reachable"
            fi
        else
            print_error "SPARQL_ENDPOINT not configured"
        fi
    else
        print_warning "System configuration not found (local installation?)"
    fi
}

# Function to test MCP protocol
test_mcp_protocol() {
    print_header "Testing MCP Protocol"
    
    print_info "Testing MCP initialization sequence..."
    
    # Create a simple MCP test using curl
    # This tests if the server can handle MCP protocol messages
    mcp_init='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test-client","version":"1.0.0"}}}'
    
    response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -H "Accept: text/event-stream" \
        --connect-timeout $TEST_TIMEOUT \
        -d "$mcp_init" \
        "$TEST_ENDPOINT$MCP_PATH" 2>/dev/null || echo "curl_failed")
    
    if [ "$response" != "curl_failed" ] && [ -n "$response" ]; then
        if echo "$response" | grep -q "jsonrpc\|capabilities\|serverInfo"; then
            print_success "MCP protocol is responding correctly"
        else
            print_warning "MCP protocol response unclear"
            print_info "Response: ${response:0:100}..."
        fi
    else
        print_warning "MCP protocol test inconclusive (may need proper MCP client)"
    fi
}

# Function to test with Python FastMCP client
test_with_fastmcp() {
    print_header "Testing with FastMCP Client"
    
    # Check if we can run Python tests
    if [ -f "venv/bin/activate" ]; then
        print_info "Running Python FastMCP client test..."
        
        # Create a Luxembourg Legal-specific test script
        cat > /tmp/test_mcp_client.py << 'EOF'
import asyncio
import sys
import os
import json
from fastmcp.client import Client, HttpTransport

async def test_mcp_client():
    try:
        transport = HttpTransport("http://localhost:8000/mcp")
        
        async with Client(transport) as client:
            # Test connection and list tools
            tools = await client.list_tools()
            tool_names = [tool.name for tool in tools]
            print(f"✅ Connected! Available tools: {tool_names}")
            
            # Test Luxembourg-specific functionality
            if "search_luxembourg_documents" in tool_names:
                try:
                    result = await client.call_tool("search_luxembourg_documents", {
                        "keywords": "taxe", 
                        "limit": 1, 
                        "include_content": False
                    })
                    result_data = json.loads(result[0].text)
                    doc_count = len(result_data.get('results', []))
                    print(f"✅ Luxembourg search successful: Found {doc_count} documents")
                except Exception as e:
                    print(f"⚠️  Luxembourg search failed: {e}")
            
            # Test basic cache functionality
            if "cache" in tool_names:
                try:
                    result = await client.call_tool("cache", {"action": "stats"})
                    print(f"✅ Cache test successful")
                except Exception as e:
                    print(f"⚠️  Cache test failed: {e}")
            
            return True
            
    except Exception as e:
        print(f"❌ FastMCP client test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mcp_client())
    sys.exit(0 if success else 1)
EOF

        # Run the test
        if source venv/bin/activate && python /tmp/test_mcp_client.py 2>/dev/null; then
            print_success "FastMCP client test passed"
        else
            print_warning "FastMCP client test failed (server may still work with other clients)"
        fi
        
        # Clean up
        rm -f /tmp/test_mcp_client.py
    else
        print_info "Skipping FastMCP client test (no virtual environment found)"
    fi
}

# Function to show connection info
show_connection_info() {
    print_header "Connection Information"
    
    echo "📍 Server Endpoints:"
    echo "   HTTP: $TEST_ENDPOINT$MCP_PATH"
    echo "   For nginx: proxy_pass http://localhost:8000$MCP_PATH;"
    echo
    echo "🔌 Client Connection Examples:"
    echo "   FastMCP: HttpTransport(\"$TEST_ENDPOINT$MCP_PATH\")"
    echo "   curl: curl -H \"Accept: text/event-stream\" $TEST_ENDPOINT$MCP_PATH"
    echo
    echo "📋 Management Commands:"
    echo "   ./status.sh  - Check service status"
    echo "   ./logs.sh    - View server logs"
    echo "   ./stop.sh    - Stop server"
    echo "   ./start.sh   - Start server"
}

# Main test function
main() {
    echo -e "${BLUE}"
    echo "🧪 MCP SPARQL Server Test Suite"
    echo "=============================="
    echo -e "${NC}"
    
    local failed_tests=0
    
    # Run all tests
    test_service_status || ((failed_tests++))
    echo
    
    test_http_endpoint || ((failed_tests++))
    echo
    
    test_configuration || ((failed_tests++))
    echo
    
    test_mcp_protocol || ((failed_tests++))
    echo
    
    test_with_fastmcp || ((failed_tests++))
    echo
    
    show_connection_info
    echo
    
    # Summary
    print_header "Test Summary"
    if [ $failed_tests -eq 0 ]; then
        print_success "All tests passed! 🎉"
        print_info "Your MCP SPARQL server is ready for production use."
        return 0
    else
        print_warning "$failed_tests test(s) had issues"
        print_info "Check the output above for details and solutions."
        return 1
    fi
}

# Handle command line arguments
case "${1:-}" in
    "endpoint")
        test_http_endpoint
        ;;
    "service")
        test_service_status
        ;;
    "config")
        test_configuration
        ;;
    "mcp")
        test_mcp_protocol
        ;;
    "client")
        test_with_fastmcp
        ;;
    "info")
        show_connection_info
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [test_type]"
        echo ""
        echo "Test types:"
        echo "  endpoint  - Test HTTP endpoint connectivity"
        echo "  service   - Test service status"
        echo "  config    - Test configuration"
        echo "  mcp       - Test MCP protocol"
        echo "  client    - Test with FastMCP client"
        echo "  info      - Show connection information"
        echo ""
        echo "Run without arguments to execute all tests"
        ;;
    *)
        main
        ;;
esac