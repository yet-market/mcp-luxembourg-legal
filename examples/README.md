# Luxembourg Legal MCP Examples

This directory contains example scripts for testing and using the Luxembourg Legal MCP server with various AI platforms.

## Setup

1. Create a `.env` file in the project root:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

2. Install additional dependencies:
```bash
pip install openai python-dotenv
```

## Examples

### `openai_test.py`

Tests the Luxembourg Legal MCP server integration with OpenAI's API.

**Features:**
- Tests French language legal queries
- Validates MCP server connectivity  
- Shows tool usage and responses
- Demonstrates Luxembourg-specific legal searches

**Usage:**
```bash
cd examples
python openai_test.py
```

**Test Queries:**
- Tax documentation search ("taxe")
- Company law information ("sociétés")
- Environmental regulations ("environnement") 
- Employment law ("travail et emploi")

## MCP Configuration

The examples use this OpenAI MCP configuration:

```json
{
  "type": "mcp",
  "server_label": "luxembourg_legal",
  "server_url": "https://yet-mcp-legilux.site/mcp/",
  "allowed_tools": ["search_luxembourg_documents"],
  "require_approval": "never"
}
```

## Available Tools

- **`search_luxembourg_documents`**: Search Luxembourg legal documents with content extraction
  - Keywords: Use French terms (e.g., "taxe", "société", "environnement")
  - Returns: Legal document metadata and full content
  - Source: Luxembourg government SPARQL endpoint

## Notes

- All examples use French language for Luxembourg legal documents
- The `.env` file is git-ignored for security
- MCP server must be running at the configured URL
- OpenAI API key is required for testing