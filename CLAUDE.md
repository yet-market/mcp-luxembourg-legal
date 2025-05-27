# MCP Luxembourg Legal Intelligence Server - AI Development Guide

This file contains information for AI assistants (Claude, Copilot, GPT-o3) to understand the project structure and development practices.

## 🤖 AI Co-Development

This project is co-developed with multiple AI systems:
- **Claude (Anthropic)**: Primary architecture, implementation, testing, and documentation
- **GitHub Copilot/Codex (OpenAI)**: Code completion and development acceleration
- **GPT-o3 (OpenAI)**: Advanced reasoning and complex problem-solving

## Development Philosophy

- **Human-AI Collaboration**: Leveraging AI for rapid development while maintaining human oversight
- **Domain Expertise**: Building AI-ready legal intelligence for Luxembourg government data
- **Quality First**: AI assistance enhances but doesn't replace code review and testing
- **Transparency**: Clear attribution of AI contributions in commits and documentation

## Project Overview

MCP Luxembourg Legal Intelligence Server is a specialized Python-based server that implements the Model Context Protocol (MCP) to provide intelligent access to Luxembourg legal documents, company registries, and administrative data. Unlike generic SPARQL servers, this focuses on transforming raw government data into AI-digestible legal intelligence.

## Key Architecture

- **FastMCP Framework**: Uses FastMCP for MCP protocol implementation
- **Transport Support**: Both stdio (for direct client communication) and HTTP (for web/nginx integration)
- **Luxembourg-Specific Design**: Specialized for Luxembourg legal system and data structures
- **Content Intelligence**: Automatic HTML/PDF extraction with Langchain integration
- **Semantic Processing**: Legal document understanding and relationship mapping
- **Configuration**: Pydantic-based configuration optimized for legal document processing

## Development Commands

### Testing
```bash
# Run tests with existing venv
source venv/bin/activate && python test_luxembourg_legal_server.py
```

### Running the Server
```bash
# Stdio transport (default) - Luxembourg endpoint
source venv/bin/activate && python server.py --endpoint https://data.legilux.public.lu/sparqlendpoint

# HTTP transport for Luxembourg legal data
source venv/bin/activate && python server.py --transport http --host localhost --port 8000 --endpoint https://data.legilux.public.lu/sparqlendpoint
```

### Code Quality
- Always use the existing virtual environment: `source venv/bin/activate`
- Follow Luxembourg legal domain patterns and conventions
- Update documentation when adding legal processing features
- Keep dependencies in requirements.txt up to date (especially Langchain and content extraction libs)
- Test with real Luxembourg government documents

## Transport Modes

1. **stdio**: For MCP client direct communication with legal document intelligence
2. **http**: For web integration and nginx reverse proxy for legal data APIs

## Important Files

- `server.py`: Main entry point with Luxembourg-specific command-line interface
- `luxembourg_legal_server/core/server.py`: Core legal intelligence server implementation
- `luxembourg_legal_server/core/config.py`: Luxembourg-specific configuration management
- `luxembourg_legal_server/extractors/`: Content extraction modules (HTML/PDF)
- `luxembourg_legal_server/legal/`: Legal document processing and semantic understanding
- `requirements.txt`: Python dependencies (includes Langchain, BeautifulSoup, PyPDF)
- `CHANGELOG.md`: Version history and changes
- `README.md`: User documentation focused on Luxembourg legal use cases

## Dependencies

### Core MCP Framework
- fastmcp: MCP protocol framework
- SPARQLWrapper: SPARQL endpoint communication
- pydantic: Configuration validation

### Luxembourg Legal Processing
- langchain: Document processing and content extraction
- beautifulsoup4: HTML content extraction from Luxembourg government pages
- pypdf: PDF content extraction from legal documents
- requests: HTTP client for fetching document content

### Background Processing
- python-daemon: Background process support

## Luxembourg-Specific Features

### Document Processing Pipeline
1. **SPARQL Discovery**: Execute keyword-based queries against Luxembourg data
2. **Content Extraction**: Fetch and extract HTML/PDF content from government URLs
3. **Legal Intelligence**: Process and structure content for AI consumption
4. **Relationship Mapping**: Identify connections between legal documents

### Legal Document Types
- **Laws and Regulations**: Full legal text with amendments and relationships
- **Company Registry**: Business information with complete details
- **Administrative Acts**: Government decisions and administrative documents
- **Official Publications**: Legal notices and announcements

### AI Tool Design
- `search_luxembourg_documents`: Keyword-based legal document search with full content
- `search_companies`: Company registry search with detailed information
- `search_regulations`: Regulation-specific search with legal context
- `get_entity_details`: Universal entity resolution with content fetching

## Content Extraction Strategy

### HTML Processing
- Target: `{entity_uri}/fr/html` 
- Extract: `<body>` content using BeautifulSoup
- Clean and structure legal text for AI consumption

### PDF Processing  
- Target: `{entity_uri}/fr/pdf`
- Extract: Full text using PyPDF/Langchain document loaders
- Handle legal document formatting and structure

### Caching Strategy
- Legal documents rarely change → aggressive caching (24h+ TTL)
- Cache both metadata and extracted content
- Optimize for repeated AI queries on same documents

## Development Patterns

### Legal Domain Knowledge
- Understand Luxembourg legal document structure
- Recognize legal relationships (amendments, references, hierarchies)
- Process French language legal text appropriately
- Handle various document formats from Luxembourg government

### AI-First Design
- Design tools for AI agent consumption
- Provide rich, contextual results instead of raw data
- Include relationships and semantic information
- Structure results for natural language processing

### Error Handling
- Graceful handling of unavailable documents
- Fallback strategies for content extraction failures
- Logging for legal document processing issues
- User-friendly error messages for legal queries

## Testing Strategy

### Document Processing Tests
- Test HTML extraction from real Luxembourg government pages
- Test PDF extraction from legal documents
- Validate SPARQL query generation for legal searches
- Test content caching and retrieval

### Legal Intelligence Tests
- Verify legal document classification
- Test relationship detection between documents
- Validate semantic processing of legal content
- Test AI tool responses for legal queries

### Integration Tests
- End-to-end legal document search workflows
- MCP protocol compliance with legal content
- Performance testing with large legal document sets
- Real-world usage scenarios with AI clients