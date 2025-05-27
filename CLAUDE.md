# MCP SPARQL Server - AI Development Guide

This file contains information for AI assistants (Claude, Copilot, GPT-o3) to understand the project structure and development practices.

## 🤖 AI Co-Development

This project is co-developed with multiple AI systems:
- **Claude (Anthropic)**: Primary architecture, implementation, testing, and documentation
- **GitHub Copilot/Codex (OpenAI)**: Code completion and development acceleration
- **GPT-o3 (OpenAI)**: Advanced reasoning and complex problem-solving

## Development Philosophy

- **Human-AI Collaboration**: Leveraging AI for rapid development while maintaining human oversight
- **Quality First**: AI assistance enhances but doesn't replace code review and testing
- **Transparency**: Clear attribution of AI contributions in commits and documentation

## Project Overview

MCP SPARQL Server is a Python-based server that implements the Model Context Protocol (MCP) to provide SPARQL query capabilities. The server supports both stdio and HTTP transports for different deployment scenarios.

## Key Architecture

- **FastMCP Framework**: Uses FastMCP for MCP protocol implementation
- **Transport Support**: Both stdio (for direct client communication) and HTTP (for web/nginx integration)
- **Modular Design**: Separated into core, formatters, and cache modules
- **Configuration**: Pydantic-based configuration with environment variable support

## Development Commands

### Testing
```bash
# Run tests with existing venv
source venv/bin/activate && python test_sparql_server.py
```

### Running the Server
```bash
# Stdio transport (default)
source venv/bin/activate && python server.py --endpoint https://dbpedia.org/sparql

# HTTP transport
source venv/bin/activate && python server.py --transport http --host localhost --port 8000 --endpoint https://dbpedia.org/sparql
```

### Code Quality
- Always use the existing virtual environment: `source venv/bin/activate`
- Follow the existing code style and patterns
- Update documentation when adding features
- Keep dependencies in requirements.txt up to date

## Transport Modes

1. **stdio**: For MCP client direct communication
2. **http**: For web integration and nginx reverse proxy

## Important Files

- `server.py`: Main entry point with command-line interface
- `sparql_server/core/server.py`: Core SPARQL server implementation
- `sparql_server/core/config.py`: Configuration management
- `requirements.txt`: Python dependencies
- `CHANGELOG.md`: Version history and changes
- `README.md`: User documentation

## Dependencies

- fastmcp: MCP protocol framework
- SPARQLWrapper: SPARQL endpoint communication
- pydantic: Configuration validation
- python-daemon: Background process support