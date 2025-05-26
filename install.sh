#!/bin/bash
# Installation script for MCP SPARQL Server

set -e

# Check if running as root for systemd service installation
if [ "$EUID" -ne 0 ]; then
    echo "For full installation with systemd service, please run as root."
    echo "Continuing with local installation only..."
    INSTALL_SYSTEMD=false
else
    INSTALL_SYSTEMD=true
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install the package
echo "Installing MCP SPARQL Server..."
pip install -e .

# If running as root, install systemd service
if [ "$INSTALL_SYSTEMD" = true ]; then
    echo "Installing systemd service..."
    
    # Copy service file to systemd directory
    cp sparql-server.service /etc/systemd/system/
    
    # Create log directory if it doesn't exist
    mkdir -p /var/log/mcp-sparql
    
    # Create config directory
    mkdir -p /etc/mcp-sparql
    
    # Create a default environment file
    cat > /etc/mcp-sparql/env <<EOF
# MCP SPARQL Server environment configuration

# SPARQL endpoint URL (required)
SPARQL_ENDPOINT=https://data.legilux.public.lu/sparqlendpoint

# Request timeout in seconds
SPARQL_TIMEOUT=30

# Maximum number of results
SPARQL_MAX_RESULTS=1000

# Cache configuration
SPARQL_CACHE_ENABLED=true
SPARQL_CACHE_TTL=300
SPARQL_CACHE_MAX_SIZE=100
SPARQL_CACHE_STRATEGY=lru

# Result formatting
SPARQL_FORMAT=json
SPARQL_PRETTY_PRINT=false
SPARQL_INCLUDE_METADATA=true
EOF
    
    # Update the service file to use the environment file
    sed -i 's|Environment=SPARQL_ENDPOINT=.*|EnvironmentFile=/etc/mcp-sparql/env|' /etc/systemd/system/sparql-server.service
    
    # Reload systemd
    systemctl daemon-reload
    
    echo "Systemd service installed."
    echo "To start the service:"
    echo "  1. Edit configuration in /etc/mcp-sparql/env"
    echo "  2. Run: systemctl start sparql-server"
    echo "  3. To enable on boot: systemctl enable sparql-server"
    echo "  4. To check logs: journalctl -u sparql-server"
fi

echo "Installation complete."
echo "You can run the server with: mcp-server-sparql --endpoint YOUR_ENDPOINT"