# MCP SPARQL Server

<div align="center">

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)

*A flexible and powerful SPARQL-enabled server for MCP (Model Context Protocol)*

</div>

## 🌟 Overview

MCP SPARQL Server is a high-performance, configurable server that connects to any SPARQL endpoint and provides enhanced functionality including result formatting and caching. It's built on top of the FastMCP framework implementing the Model Context Protocol (MCP) to provide a seamless interface for AI assistants to query semantic data.

## ✨ Features

- **Universal Endpoint Support**: Connect to any SPARQL-compliant endpoint
- **Full SPARQL Support**: Execute any valid SPARQL query (SELECT, ASK, CONSTRUCT, DESCRIBE)
- **Intelligent Result Formatting**:
  - Standard JSON (compatible with standard SPARQL clients)
  - Simplified JSON (easier to work with in applications)
  - Tabular format (ready for display in UI tables)
- **High-Performance Caching**:
  - Multiple cache strategies (LRU, LFU, FIFO)
  - Configurable TTL (time-to-live)
  - Cache management tools
- **Flexible Deployment Options**:
  - Run in foreground mode with stdio or HTTP transport
  - Run as a background daemon
  - Deploy as a systemd service
  - HTTP server mode for nginx reverse proxy integration
- **Comprehensive Configuration**:
  - Command-line arguments
  - Environment variables
  - No hardcoded values

## 📋 Requirements

- Python 3.8 or newer
- `SPARQLWrapper` library
- `fastmcp` framework
- `pydantic` for configuration
- `python-daemon` for background execution

## 🚀 Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/yet-market/yet-sparql-mcp-server.git
cd yet-sparql-mcp-server

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### From PyPI

```bash
pip install mcp-server-sparql
```

### Using the Installation Script

For a full installation with systemd service setup:

```bash
# Download the repository
git clone https://github.com/yet-market/yet-sparql-mcp-server.git
cd yet-sparql-mcp-server

# Run the installation script (as root for systemd service)
sudo ./install.sh
```

The installer automatically:
- Sets up virtual environment and dependencies
- Creates and starts systemd services
- Provides management scripts for easy control
- Configures the HTTP service for nginx integration

### Quick Management

After installation, use the provided scripts:

```bash
# Check status
./status.sh

# Start/stop services
./start.sh [stdio|http]    # Start service (http is default)
./stop.sh [stdio|http]     # Stop service
./logs.sh [stdio|http]     # View logs

# Examples
./start.sh http            # Start HTTP service for nginx
./logs.sh http             # View HTTP service logs
./test.sh                  # Test server functionality
./stop.sh                  # Stop all services
```

### Testing Your Installation

Test your server with the built-in test suite:

```bash
# Run comprehensive tests
./test.sh

# Run specific tests
./test.sh endpoint         # Test HTTP connectivity
./test.sh service          # Test service status
./test.sh config           # Test configuration
./test.sh mcp              # Test MCP protocol
./test.sh client           # Test with FastMCP client
./test.sh info             # Show connection info
```

The test script validates:
- ✅ Service status and health
- ✅ HTTP endpoint connectivity  
- ✅ MCP protocol compliance
- ✅ Configuration validity
- ✅ SPARQL endpoint reachability
- ✅ FastMCP client integration

## 🔍 Usage

### Basic Usage (stdio transport)

Start the server by specifying a SPARQL endpoint:

```bash
python server.py --endpoint https://dbpedia.org/sparql
```

### HTTP Server Mode (for nginx/web integration)

Run the server as an HTTP server:

```bash
# Basic HTTP server
python server.py --transport http --endpoint https://dbpedia.org/sparql

# Custom host and port
python server.py --transport http --host 0.0.0.0 --port 8080 --endpoint https://dbpedia.org/sparql

# Using environment variables
export MCP_TRANSPORT=http
export MCP_HOST=0.0.0.0
export MCP_PORT=8000
export SPARQL_ENDPOINT=https://dbpedia.org/sparql
python server.py
```

### Running as a Daemon

To run the server as a background process (stdio transport):

```bash
python server.py --endpoint https://dbpedia.org/sparql --daemon \
  --log-file /var/log/mcp-sparql.log \
  --pid-file /var/run/mcp-sparql.pid
```

To run the HTTP server as a daemon:

```bash
python server.py --transport http --host 0.0.0.0 --port 8000 \
  --endpoint https://dbpedia.org/sparql --daemon \
  --log-file /var/log/mcp-sparql.log \
  --pid-file /var/run/mcp-sparql.pid
```

### Using with Systemd

If installed with systemd support:

1. Configure your endpoint in the environment file:
   ```bash
   sudo nano /etc/mcp-sparql/env
   ```

2. Start the service:
   ```bash
   sudo systemctl start sparql-server
   ```

3. Enable on boot:
   ```bash
   sudo systemctl enable sparql-server
   ```

### Client Query Examples

After starting the server, you can use it with any MCP-compatible client or through the FastMCP client:

#### Using FastMCP Client with stdio transport (Python)

```python
import asyncio
from fastmcp.client import Client, PythonStdioTransport

async def query_server():
    # Connect to the server
    transport = PythonStdioTransport(
        script_path="server.py",
        args=["--endpoint", "https://dbpedia.org/sparql"]
    )
    
    async with Client(transport) as client:
        # Execute a SPARQL query
        result = await client.call_tool("query", {
            "query_string": "SELECT * WHERE { ?s ?p ?o } LIMIT 5",
            "format": "simplified"
        })
        
        print(result[0].text)

asyncio.run(query_server())
```

#### Using FastMCP Client with HTTP transport (Python)

```python
import asyncio
from fastmcp.client import Client, HttpTransport

async def query_server():
    # Connect to HTTP server
    transport = HttpTransport("http://localhost:8000")
    
    async with Client(transport) as client:
        # Execute a SPARQL query
        result = await client.call_tool("query", {
            "query_string": "SELECT * WHERE { ?s ?p ?o } LIMIT 5",
            "format": "simplified"
        })
        
        print(result[0].text)

asyncio.run(query_server())
```

#### Query with Different Formats

```python
# JSON format (default)
result = await client.call_tool("query", {
    "query_string": "SELECT * WHERE { ?s ?p ?o } LIMIT 5",
    "format": "json"
})

# Tabular format
result = await client.call_tool("query", {
    "query_string": "SELECT * WHERE { ?s ?p ?o } LIMIT 5",
    "format": "tabular"
})
```

#### Cache Management

```python
# Get cache statistics
cache_stats = await client.call_tool("cache", {"action": "stats"})

# Clear the cache
cache_clear = await client.call_tool("cache", {"action": "clear"})
```

## ⚙️ Configuration

### Command-line Arguments

<table>
<thead>
  <tr>
    <th>Argument</th>
    <th>Description</th>
    <th>Default</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td><code>--endpoint URL</code></td>
    <td>SPARQL endpoint URL</td>
    <td>Required</td>
  </tr>
  <tr>
    <td><code>--timeout SECONDS</code></td>
    <td>Request timeout in seconds</td>
    <td>30</td>
  </tr>
  <tr>
    <td><code>--format FORMAT</code></td>
    <td>Result format (json, simplified, tabular)</td>
    <td>json</td>
  </tr>
  <tr>
    <td><code>--cache-enabled BOOL</code></td>
    <td>Enable result caching</td>
    <td>true</td>
  </tr>
  <tr>
    <td><code>--cache-ttl SECONDS</code></td>
    <td>Cache time-to-live in seconds</td>
    <td>300</td>
  </tr>
  <tr>
    <td><code>--cache-max-size SIZE</code></td>
    <td>Maximum cache size</td>
    <td>100</td>
  </tr>
  <tr>
    <td><code>--cache-strategy STRATEGY</code></td>
    <td>Cache replacement strategy (lru, lfu, fifo)</td>
    <td>lru</td>
  </tr>
  <tr>
    <td><code>--pretty-print</code></td>
    <td>Pretty print JSON output</td>
    <td>false</td>
  </tr>
  <tr>
    <td><code>--include-metadata BOOL</code></td>
    <td>Include query metadata in results</td>
    <td>true</td>
  </tr>
  <tr>
    <td><code>--daemon</code></td>
    <td>Run as a background daemon</td>
    <td>false</td>
  </tr>
  <tr>
    <td><code>--log-file FILE</code></td>
    <td>Log file location when running as a daemon</td>
    <td>/var/log/mcp-sparql-server.log</td>
  </tr>
  <tr>
    <td><code>--pid-file FILE</code></td>
    <td>PID file location when running as a daemon</td>
    <td>/var/run/mcp-sparql-server.pid</td>
  </tr>
  <tr>
    <td><code>--transport TRANSPORT</code></td>
    <td>Transport type (stdio or http)</td>
    <td>stdio</td>
  </tr>
  <tr>
    <td><code>--host HOST</code></td>
    <td>Host to bind HTTP server to</td>
    <td>localhost</td>
  </tr>
  <tr>
    <td><code>--port PORT</code></td>
    <td>Port to bind HTTP server to</td>
    <td>8000</td>
  </tr>
</tbody>
</table>

### Environment Variables

<table>
<thead>
  <tr>
    <th>Variable</th>
    <th>Description</th>
    <th>Default</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td><code>SPARQL_ENDPOINT</code></td>
    <td>SPARQL endpoint URL</td>
    <td>None (required)</td>
  </tr>
  <tr>
    <td><code>SPARQL_TIMEOUT</code></td>
    <td>Request timeout in seconds</td>
    <td>30</td>
  </tr>
  <tr>
    <td><code>SPARQL_FORMAT</code></td>
    <td>Default result format</td>
    <td>json</td>
  </tr>
  <tr>
    <td><code>SPARQL_CACHE_ENABLED</code></td>
    <td>Enable caching</td>
    <td>true</td>
  </tr>
  <tr>
    <td><code>SPARQL_CACHE_TTL</code></td>
    <td>Cache time-to-live in seconds</td>
    <td>300</td>
  </tr>
  <tr>
    <td><code>SPARQL_CACHE_MAX_SIZE</code></td>
    <td>Maximum cache size</td>
    <td>100</td>
  </tr>
  <tr>
    <td><code>SPARQL_CACHE_STRATEGY</code></td>
    <td>Cache replacement strategy</td>
    <td>lru</td>
  </tr>
  <tr>
    <td><code>SPARQL_PRETTY_PRINT</code></td>
    <td>Pretty print JSON output</td>
    <td>false</td>
  </tr>
  <tr>
    <td><code>SPARQL_INCLUDE_METADATA</code></td>
    <td>Include query metadata in results</td>
    <td>true</td>
  </tr>
  <tr>
    <td><code>MCP_TRANSPORT</code></td>
    <td>Transport type (stdio or http)</td>
    <td>stdio</td>
  </tr>
  <tr>
    <td><code>MCP_HOST</code></td>
    <td>Host to bind HTTP server to</td>
    <td>localhost</td>
  </tr>
  <tr>
    <td><code>MCP_PORT</code></td>
    <td>Port to bind HTTP server to</td>
    <td>8000</td>
  </tr>
</tbody>
</table>

## 🌐 Nginx Integration

When using HTTP transport, you can integrate the server with nginx as a reverse proxy:

### 1. Start the server in HTTP mode

```bash
python server.py --transport http --host localhost --port 8000 --endpoint https://your-sparql-endpoint.com/sparql
```

### 2. Configure nginx

Add this configuration to your nginx server block:

```nginx
upstream mcp_sparql {
    server localhost:8000;
    # Add more servers for load balancing if needed
    # server localhost:8001;
    # server localhost:8002;
}

server {
    listen 80;
    server_name your-domain.com;

    location /api/sparql {
        proxy_pass http://mcp_sparql;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Optional: Add CORS headers
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
        add_header Access-Control-Allow-Headers "Content-Type, Authorization";
    }
}
```

### 3. Production deployment with systemd

Create a systemd service for HTTP mode:

```ini
# /etc/systemd/system/mcp-sparql-http.service
[Unit]
Description=MCP SPARQL Server (HTTP)
After=network.target

[Service]
Type=simple
User=mcp-sparql
Group=mcp-sparql
WorkingDirectory=/opt/mcp-sparql
Environment=MCP_TRANSPORT=http
Environment=MCP_HOST=localhost
Environment=MCP_PORT=8000
Environment=SPARQL_ENDPOINT=https://your-sparql-endpoint.com/sparql
ExecStart=/opt/mcp-sparql/venv/bin/python server.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable mcp-sparql-http
sudo systemctl start mcp-sparql-http
```

## 📊 Result Formats

The server supports three different output formats:

### 1. JSON Format (default)

Returns the standard SPARQL JSON results format with optional metadata.

```json
{
  "head": {
    "vars": ["s", "p", "o"]
  },
  "results": {
    "bindings": [
      {
        "s": { "type": "uri", "value": "http://example.org/resource" },
        "p": { "type": "uri", "value": "http://example.org/property" },
        "o": { "type": "literal", "value": "Example Value" }
      }
    ]
  },
  "metadata": {
    "variables": ["s", "p", "o"],
    "count": 1,
    "query": "SELECT * WHERE { ?s ?p ?o } LIMIT 1"
  }
}
```

### 2. Simplified Format

Returns a simplified JSON structure that's easier to work with, converting variable bindings into simple key-value objects.

```json
{
  "type": "SELECT",
  "results": [
    {
      "s": "http://example.org/resource",
      "p": "http://example.org/property",
      "o": "Example Value"
    }
  ],
  "metadata": {
    "variables": ["s", "p", "o"],
    "count": 1,
    "query": "SELECT * WHERE { ?s ?p ?o } LIMIT 1"
  }
}
```

### 3. Tabular Format

Returns results in a tabular format with columns and rows, suitable for table display.

```json
{
  "type": "SELECT",
  "columns": [
    { "name": "s", "label": "s" },
    { "name": "p", "label": "p" },
    { "name": "o", "label": "o" }
  ],
  "rows": [
    [
      "http://example.org/resource",
      "http://example.org/property",
      "Example Value"
    ]
  ],
  "metadata": {
    "variables": ["s", "p", "o"],
    "count": 1,
    "query": "SELECT * WHERE { ?s ?p ?o } LIMIT 1"
  }
}
```

## 🔄 Cache Strategies

The server supports three cache replacement strategies:

### 1. LRU (Least Recently Used)

Evicts the least recently accessed items first. This is the default strategy and works well for most scenarios, as it prioritizes keeping recently accessed items in the cache.

### 2. LFU (Least Frequently Used)

Evicts the least frequently accessed items first. This strategy is good for scenarios where some queries are much more common than others, as it prioritizes keeping frequently accessed items in the cache.

### 3. FIFO (First In First Out)

Evicts the oldest items first, regardless of access patterns. This strategy is simpler and can be useful when you want a purely time-based caching approach.

## 🔍 Advanced SPARQL Examples

The server supports all SPARQL features. Here are some example queries you can try:

### Basic Triple Pattern

```sparql
SELECT * WHERE { ?s ?p ?o } LIMIT 10
```

### Filtering by Property Type

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?subject ?label
WHERE {
    ?subject rdf:type rdfs:Class ;
             rdfs:label ?label .
}
LIMIT 10
```

### Using Regular Expressions

```sparql
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?person ?name
WHERE {
    ?person foaf:name ?name .
    FILTER(REGEX(?name, "Smith", "i"))
}
LIMIT 10
```

### Complex Query with Multiple Patterns

```sparql
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?city ?name ?population ?country ?countryName
WHERE {
    ?city a dbo:City ;
          rdfs:label ?name ;
          dbo:population ?population ;
          dbo:country ?country .
    ?country rdfs:label ?countryName .
    FILTER(?population > 1000000)
    FILTER(LANG(?name) = 'en')
    FILTER(LANG(?countryName) = 'en')
}
ORDER BY DESC(?population)
LIMIT 10
```

## ⚠️ Troubleshooting

### Common Issues

- **Connection refused**: Check that the SPARQL endpoint URL is correct and accessible
- **Query timeout**: Increase the timeout value with `--timeout` option
- **Memory issues with large result sets**: Add LIMIT clause to your queries or reduce cache size
- **Permission denied for log/pid files**: Check directory permissions or run with appropriate privileges

### Logging

When running in foreground mode, logs are output to the console. When running as a daemon, logs are written to the specified log file (default: `/var/log/mcp-sparql-server.log`).

To increase verbosity, you can set the Python logging level in the source code.

## 🛠️ Development

### Project Structure

```
mcp-server-sparql/
├── sparql_server/             # Main package
│   ├── core/                  # Core functionality
│   │   ├── __init__.py        # Package exports
│   │   ├── config.py          # Configuration management
│   │   └── server.py          # Main SPARQL server
│   ├── formatters/            # Result formatters
│   │   ├── __init__.py        # Package exports
│   │   ├── formatter.py       # Base formatter class
│   │   ├── json_formatter.py  # JSON formatter
│   │   ├── simplified_formatter.py # Simplified JSON formatter
│   │   └── tabular_formatter.py # Tabular formatter
│   ├── cache/                 # Caching implementation
│   │   ├── __init__.py        # Package exports
│   │   ├── query_cache.py     # Base cache interface
│   │   ├── lru_cache.py       # LRU cache implementation
│   │   ├── lfu_cache.py       # LFU cache implementation
│   │   └── fifo_cache.py      # FIFO cache implementation
│   └── __init__.py            # Package exports
├── server.py                  # Main entry point
├── setup.py                   # Package setup
├── install.sh                 # Installation script
├── requirements.txt           # Python dependencies
├── sparql-server.service      # Systemd service file
├── README.md                  # This file
└── LICENSE                    # License file
```

### Running Tests

```bash
# Test stdio transport
python test_sparql_server.py

# Test HTTP transport (start server first)
# Terminal 1:
python server.py --transport http --endpoint https://dbpedia.org/sparql
# Terminal 2:
# Run HTTP-specific tests (if available)
```

## 🔒 Security Considerations

- The server doesn't implement authentication or authorization - it relies on the security of the underlying SPARQL endpoint
- For production use, consider deploying behind a secure proxy
- Be careful with untrusted queries as they could potentially be resource-intensive

## 📄 License

This project is licensed under a dual-license model:

- **Open Source**: GNU Affero General Public License v3.0 (AGPL-3.0) for open source use
- **Commercial**: Proprietary commercial license available for commercial or proprietary use

See the [LICENSE](LICENSE) file for complete details.

This software was imagined and developed by Temkit Sid-Ali for Yet.lu.

## 🚀 Roadmap

We have exciting plans for the future! Check out our [detailed roadmap](ROADMAP.md) to see what's coming next, including:

- 🔒 Enhanced security and authentication
- 🌐 Web interface for query exploration
- 🤖 AI-powered natural language to SPARQL conversion
- 📊 Advanced data visualization and analytics
- 🏢 Enterprise features and scalability improvements

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See our [Contributing Guide](CONTRIBUTING.md) for detailed development setup and guidelines.

## 🙏 Acknowledgments

This project is built on top of several excellent open source projects:

- **[FastMCP](https://github.com/jlowin/fastmcp)** - High-level Python framework for building MCP servers and clients by Joel Lowin
- **[SPARQLWrapper](https://github.com/RDFLib/sparqlwrapper)** - SPARQL endpoint interface for Python by the RDFLib team
- **[Pydantic](https://github.com/pydantic/pydantic)** - Data validation using Python type hints by Samuel Colvin and the Pydantic team
- **[python-daemon](https://github.com/breezy-team/python-daemon)** - Library for making Unix daemon processes

Special thanks to:
- The **Model Context Protocol (MCP)** community for developing the protocol specification
- **Anthropic** for their work on AI assistants and the MCP ecosystem
- The **semantic web** and **RDF** communities for their foundational work
- **W3C** for the SPARQL specification and standards

## 📬 Contact

- GitHub Issues: [https://github.com/yet-market/yet-sparql-mcp-server/issues](https://github.com/yet-market/yet-sparql-mcp-server/issues)
- Website: [https://yet.lu](https://yet.lu)
- Development: dev@yet.lu
- Commercial licensing: legal@yet.lu

---

<div align="center">
  <sub>Built with ❤️ by Temkit Sid-Ali for <a href="https://yet.lu">Yet.lu</a></sub>
  <br>
  <sub>© 2025 <a href="https://yet.lu">Yet.lu</a> - All rights reserved</sub>
</div>