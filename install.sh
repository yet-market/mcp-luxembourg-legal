#!/bin/bash
# Installation script for MCP SPARQL Server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default installation directory
INSTALL_DIR="/opt/mcp-sparql"
SERVICE_USER="mcp-sparql"

# Print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root for systemd service installation
if [ "$EUID" -ne 0 ]; then
    print_warning "For full installation with systemd service, please run as root."
    print_warning "Continuing with local installation only..."
    INSTALL_SYSTEMD=false
else
    INSTALL_SYSTEMD=true
fi

# Check Python version
print_status "Checking Python version..."
if ! python3 --version | grep -E "Python 3\.[8-9]|Python 3\.1[0-9]" > /dev/null; then
    print_error "Python 3.8+ is required"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is required but not installed"
    exit 1
fi

# If installing system-wide, create installation directory and user
if [ "$INSTALL_SYSTEMD" = true ]; then
    print_status "Setting up system installation..."
    
    # Create installation directory
    mkdir -p "$INSTALL_DIR"
    
    # Create service user if it doesn't exist
    if ! id "$SERVICE_USER" &>/dev/null; then
        useradd --system --shell /bin/false --home-dir "$INSTALL_DIR" --create-home "$SERVICE_USER"
        print_status "Created user: $SERVICE_USER"
    fi
    
    # Copy project files to installation directory
    cp -r . "$INSTALL_DIR/"
    chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
    
    cd "$INSTALL_DIR"
fi

# Create virtual environment
print_status "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt

# If running as root, install systemd service
if [ "$INSTALL_SYSTEMD" = true ]; then
    print_status "Installing systemd service..."
    
    # Create log directory
    mkdir -p /var/log/mcp-sparql
    chown "$SERVICE_USER:$SERVICE_USER" /var/log/mcp-sparql
    
    # Create config directory
    mkdir -p /etc/mcp-sparql
    
    # Create a default environment file
    cat > /etc/mcp-sparql/env <<EOF
# MCP SPARQL Server environment configuration

# SPARQL endpoint URL (required)
SPARQL_ENDPOINT=https://dbpedia.org/sparql

# Transport configuration
MCP_TRANSPORT=stdio
MCP_HOST=localhost
MCP_PORT=8000

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
    
    # Create systemd service file
    cat > /etc/systemd/system/mcp-sparql.service <<EOF
[Unit]
Description=MCP SPARQL Server
After=network.target
Documentation=https://github.com/yet-market/yet-sparql-mcp-server

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
EnvironmentFile=/etc/mcp-sparql/env
ExecStart=$INSTALL_DIR/venv/bin/python server.py
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3
TimeoutStopSec=10

# Sandboxing
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/log/mcp-sparql
PrivateTmp=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true

# Limits
LimitNOFILE=65536
LimitNPROC=32768

[Install]
WantedBy=multi-user.target
EOF

    # Create HTTP service variant
    cat > /etc/systemd/system/mcp-sparql-http.service <<EOF
[Unit]
Description=MCP SPARQL Server (HTTP)
After=network.target
Documentation=https://github.com/yet-market/yet-sparql-mcp-server

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
EnvironmentFile=/etc/mcp-sparql/env
ExecStart=$INSTALL_DIR/venv/bin/python server.py --transport streamable-http --host localhost --port 8000
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3
TimeoutStopSec=10

# Sandboxing
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/log/mcp-sparql
PrivateTmp=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true

# Limits
LimitNOFILE=65536
LimitNPROC=32768

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd
    systemctl daemon-reload
    
    print_status "Systemd services installed successfully!"
    echo
    echo "Available services:"
    echo "  - mcp-sparql.service      (stdio transport)"
    echo "  - mcp-sparql-http.service (HTTP transport for nginx)"
    echo
    echo "Configuration:"
    echo "  1. Edit configuration in /etc/mcp-sparql/env"
    echo "  2. Set your SPARQL_ENDPOINT"
    echo
    echo "For stdio transport:"
    echo "  systemctl start mcp-sparql"
    echo "  systemctl enable mcp-sparql"
    echo
    echo "For HTTP transport (nginx integration):"
    echo "  systemctl start mcp-sparql-http"
    echo "  systemctl enable mcp-sparql-http"
    echo
    echo "Check logs:"
    echo "  journalctl -u mcp-sparql -f"
    echo "  journalctl -u mcp-sparql-http -f"
    
else
    print_status "Local installation complete!"
    echo
    echo "To run the server:"
    echo "  source venv/bin/activate"
    echo "  python server.py --endpoint YOUR_SPARQL_ENDPOINT"
    echo
    echo "For HTTP mode:"
    echo "  python server.py --transport streamable-http --host localhost --port 8000 --endpoint YOUR_SPARQL_ENDPOINT"
fi

print_status "Installation completed successfully!"