# MCP Luxembourg Legal Intelligence Server

<div align="center">

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)

*AI-powered legal document intelligence server for Luxembourg government data*

</div>

## 🌟 Overview

MCP Luxembourg Legal Intelligence Server is a specialized MCP (Model Context Protocol) server that transforms raw Luxembourg government data into AI-digestible legal intelligence. Built specifically for accessing and processing Luxembourg's legal documents, company registries, and administrative data through intelligent content extraction and semantic processing.

## ✨ Key Features

- **🇱🇺 Luxembourg Legal Focus**: Specialized tools for Luxembourg legal system
- **📄 Smart Document Processing**: Automatic HTML and PDF content extraction
- **🧠 AI-Ready Content**: Transforms raw government data into meaningful, contextual information
- **🔍 Semantic Search**: Domain-specific search tools (`search_luxembourg_documents`)
- **📊 Rich Content Extraction**: Full text extraction with metadata and relationships
- **⚡ Intelligent Caching**: Optimized for legal documents (content rarely changes)
- **🌐 Multi-format Support**: HTML, PDF, and structured data integration
- **🔄 Content Transformation**: Converts URIs to human-readable legal content

## 🎯 Purpose

Unlike generic SPARQL servers, this server is built for AI agents that need to understand and work with Luxembourg legal information. It bridges the gap between raw government data and AI-consumable knowledge.

## 📋 Requirements

- Python 3.8 or newer
- `fastmcp` framework
- `langchain` for document processing
- `beautifulsoup4` for HTML extraction
- `pypdf` for PDF processing
- `SPARQLWrapper` for SPARQL queries
- `pydantic` for configuration

## 🚀 Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/yet-market/mcp-luxembourg-legal.git
cd mcp-luxembourg-legal

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Quick Start

```bash
# Start the server
python server.py --endpoint https://data.legilux.public.lu/sparqlendpoint

# Using HTTP transport for web integration
python server.py --transport http --endpoint https://data.legilux.public.lu/sparqlendpoint
```

## 🔍 Usage

### Luxembourg-Specific Tools

The server provides specialized tools designed for Luxembourg legal data:

#### Search Legal Documents

```python
# Search for tax-related laws with full content
result = await client.call_tool("search_luxembourg_documents", {
    "keyword": "taxe",
    "include_content": True,
    "content_preference": "html"  # or "pdf" or "both"
})
```

#### Search Luxembourg Legal Documents

```python
# Search for legal documents with full content extraction
result = await client.call_tool("search_luxembourg_documents", {
    "keywords": "taxe",
    "limit": 10,
    "include_content": True
})
```

### Example Client Usage

```python
import asyncio
from fastmcp.client import Client, PythonStdioTransport

async def query_luxembourg_legal():
    transport = PythonStdioTransport(
        script_path="server.py",
        args=["--endpoint", "https://data.legilux.public.lu/sparqlendpoint"]
    )
    
    async with Client(transport) as client:
        # Search for tax regulations
        result = await client.call_tool("search_luxembourg_documents", {
            "keywords": "taxe",
            "include_content": True
        })
        
        # Parse the JSON response
        import json
        result_data = json.loads(result[0].text)
        
        print("Luxembourg Tax Regulations:")
        for doc in result_data['results']:
            print(f"- {doc['title']} ({doc['date']})")
            if doc.get('content'):
                print(f"  Content: {doc['content'][:200]}...")

asyncio.run(query_luxembourg_legal())
```

## 🛠️ Document Processing Pipeline

### Phase 1: SPARQL Discovery
1. Execute keyword-based SPARQL queries
2. Retrieve document metadata (URIs, dates, titles, types)
3. Deduplicate results by entity URI

### Phase 2: Content Extraction
1. For each document URI:
   - Try `{uri}/fr/html` → extract `<body>` content
   - If no content: try `{uri}/fr/pdf` → extract PDF text
2. Use Langchain document loaders for robust processing
3. Clean and structure extracted content

### Phase 3: Intelligence Enhancement
1. Combine metadata with full content
2. Identify relationships between documents
3. Add semantic context and legal structure
4. Return AI-ready structured results

## 📊 Result Structure

### Luxembourg Document Results

```json
{
  "results": [
    {
      "uri": "http://data.legilux.public.lu/eli/etat/leg/rgd/2025/04/10/a147/jo",
      "title": "Règlement grand-ducal du 10 avril 2025 portant fixation de la taxe de rejet des eaux usées",
      "date": "2025-04-10",
      "type": "http://data.legilux.public.lu/resource/ontology/jolux#LegalResource",
      "content": "Journal officiel du Grand-Duché de Luxembourg...",
      "content_type": "html",
      "content_source": "http://data.legilux.public.lu/eli/etat/leg/rgd/2025/04/10/a147/jo/fr/html",
      "summary": "Règlement grand-ducal portant fixation de la taxe de rejet des eaux usées pour l'année 2025",
      "document_type": "loi",
      "legal_concepts": ["tax", "environmental"]
    }
  ],
  "count": 1,
  "query_used": "PREFIX jolux: <http://data.legilux.public.lu/resource/ontology/jolux#>..."
}
```

## 🇱🇺 Luxembourg Data Sources

The server is optimized for:

- **Legal Documents**: Laws, regulations, decrees, and administrative acts
- **Company Registry**: Business registrations, modifications, and dissolutions  
- **Official Publications**: Government announcements and legal notices
- **Administrative Data**: Geographic information, classifications, and references

## ⚙️ Configuration

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
    <td><code>LUXEMBOURG_SPARQL_ENDPOINT</code></td>
    <td>Luxembourg SPARQL endpoint URL</td>
    <td>https://data.legilux.public.lu/sparqlendpoint</td>
  </tr>
  <tr>
    <td><code>CONTENT_CACHE_TTL</code></td>
    <td>Content cache duration (legal docs change rarely)</td>
    <td>86400 (24 hours)</td>
  </tr>
  <tr>
    <td><code>EXTRACTION_TIMEOUT</code></td>
    <td>Document extraction timeout</td>
    <td>60 seconds</td>
  </tr>
  <tr>
    <td><code>DEFAULT_LANGUAGE</code></td>
    <td>Preferred content language</td>
    <td>fr</td>
  </tr>
</tbody>
</table>

## 🔧 Development

### Project Structure

```
mcp-luxembourg-legal/
├── luxembourg_legal_server/        # Main package (renamed from sparql_server)
│   ├── core/                      # Core functionality
│   │   ├── config.py              # Luxembourg-specific configuration
│   │   └── server.py              # Legal intelligence server
│   ├── extractors/                # Content extraction (NEW)
│   │   ├── html_extractor.py      # HTML content extraction
│   │   ├── pdf_extractor.py       # PDF content extraction
│   │   └── content_processor.py   # Langchain-based processing
│   ├── legal/                     # Luxembourg legal processing (NEW)
│   │   ├── document_classifier.py # Legal document classification
│   │   ├── relationship_mapper.py # Document relationship detection
│   │   └── semantic_processor.py  # Legal semantic understanding
│   ├── formatters/                # Result formatters (enhanced)
│   └── cache/                     # Caching (optimized for legal content)
├── server.py                      # Main entry point (enhanced)
└── requirements.txt               # Updated dependencies
```

## 🎯 AI Integration Benefits

### For AI Agents

- **Rich Context**: Full document content instead of just URIs
- **Legal Understanding**: Structured legal information with relationships
- **Semantic Search**: Domain-specific tools that understand legal concepts
- **Multi-format Processing**: Handles various Luxembourg government document formats

### For Users

- **Natural Queries**: "Show me environmental regulations for companies"
- **Complete Answers**: Full legal text with context and relationships
- **Current Information**: Direct access to official Luxembourg government data
- **Intelligent Processing**: Automated content extraction and structuring

## 🔒 Security & Compliance

- Accesses only public Luxembourg government data
- No authentication required (public SPARQL endpoint)
- Respects government data access policies
- Implements responsible caching for public documents

## 📄 License

This project is licensed under a dual-license model:

- **Open Source**: GNU Affero General Public License v3.0 (AGPL-3.0) for open source use
- **Commercial**: Proprietary commercial license available for commercial or proprietary use

See the [LICENSE](LICENSE) file for complete details.

This software was imagined and developed by Temkit Sid-Ali for Yet.lu with AI assistance from Claude (Anthropic), GitHub Copilot/Codex (OpenAI), and GPT-o3 (OpenAI).

## 🤝 Related Projects

- **[MCP SPARQL Server](https://github.com/yet-market/yet-sparql-mcp-server)** - Generic SPARQL MCP server
- **[Luxembourg Open Data](https://data.public.lu/)** - Official Luxembourg open data portal
- **[Legilux](https://legilux.public.lu/)** - Luxembourg legal publications

## 📬 Contact

- GitHub Issues: [https://github.com/yet-market/mcp-luxembourg-legal/issues](https://github.com/yet-market/mcp-luxembourg-legal/issues)
- Website: [https://yet.lu](https://yet.lu)
- Development: dev@yet.lu
- Commercial licensing: legal@yet.lu

---

<div align="center">
  <sub>Built with ❤️ by Temkit Sid-Ali for <a href="https://yet.lu">Yet.lu</a></sub>
  <br>
  <sub>Co-developed with Claude (Anthropic), GitHub Copilot/Codex & GPT-o3 (OpenAI)</sub>
  <br>
  <sub>© 2025 <a href="https://yet.lu">Yet.lu</a> - All rights reserved</sub>
</div>