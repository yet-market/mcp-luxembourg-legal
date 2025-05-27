"""
MCP SPARQL Query Server.

This module provides a command-line interface for creating an MCP server
that can execute SPARQL queries against a specified endpoint. It supports
running as a background process and integrates with systemd.
"""

import os
import sys
import signal
import logging
import argparse
import daemon
from typing import Dict, Any, Optional, Union, List
from pathlib import Path

from fastmcp import FastMCP
from pydantic import HttpUrl

from luxembourg_legal_server.core import SPARQLServer, SPARQLConfig, ResultFormat, CacheStrategy
from luxembourg_legal_server.extractors import ContentProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.
    
    Returns:
        The parsed arguments.
    """
    parser = argparse.ArgumentParser(description="MCP SPARQL Query Server")
    
    # Server mode
    server_group = parser.add_argument_group("Server Mode")
    server_group.add_argument(
        "--daemon",
        action="store_true",
        help="Run the server as a daemon in the background"
    )
    server_group.add_argument(
        "--pid-file",
        type=str,
        help="File to store the process ID when running as a daemon"
    )
    server_group.add_argument(
        "--log-file",
        type=str,
        help="File to store logs when running as a daemon"
    )
    
    # Transport configuration
    transport_group = parser.add_argument_group("Transport Configuration")
    transport_group.add_argument(
        "--transport",
        type=str,
        choices=["stdio", "streamable-http", "sse"],
        default=os.environ.get("MCP_TRANSPORT", "stdio"),
        help="Transport type (stdio, streamable-http, or sse, default: stdio)"
    )
    transport_group.add_argument(
        "--host",
        type=str,
        default=os.environ.get("MCP_HOST", "localhost"),
        help="Host to bind HTTP server to (default: localhost)"
    )
    transport_group.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("MCP_PORT", "8000")),
        help="Port to bind HTTP server to (default: 8000)"
    )
    
    # SPARQL endpoint configuration
    endpoint_group = parser.add_argument_group("SPARQL Endpoint")
    endpoint_group.add_argument(
        "--endpoint",
        required="SPARQL_ENDPOINT" not in os.environ,
        help="SPARQL endpoint URL (e.g., https://data.legilux.public.lu/sparqlendpoint)"
    )
    endpoint_group.add_argument(
        "--timeout",
        type=int,
        default=int(os.environ.get("SPARQL_TIMEOUT", "30")),
        help="Request timeout in seconds (default: 30)"
    )
    endpoint_group.add_argument(
        "--max-results",
        type=int,
        default=int(os.environ.get("SPARQL_MAX_RESULTS", "1000")),
        help="Maximum number of results to return (default: 1000)"
    )
    
    # Cache configuration
    cache_group = parser.add_argument_group("Cache Configuration")
    cache_group.add_argument(
        "--cache-enabled",
        type=lambda x: x.lower() == "true",
        default=os.environ.get("SPARQL_CACHE_ENABLED", "true").lower() == "true",
        help="Enable caching (default: true)"
    )
    cache_group.add_argument(
        "--cache-ttl",
        type=int,
        default=int(os.environ.get("SPARQL_CACHE_TTL", "300")),
        help="Cache time-to-live in seconds (default: 300)"
    )
    cache_group.add_argument(
        "--cache-max-size",
        type=int,
        default=int(os.environ.get("SPARQL_CACHE_MAX_SIZE", "100")),
        help="Maximum cache size (default: 100)"
    )
    cache_group.add_argument(
        "--cache-strategy",
        type=str,
        choices=[strategy.value for strategy in CacheStrategy],
        default=os.environ.get("SPARQL_CACHE_STRATEGY", CacheStrategy.LRU.value),
        help=f"Cache replacement strategy (default: {CacheStrategy.LRU.value})"
    )
    
    # Result formatting configuration
    format_group = parser.add_argument_group("Result Formatting")
    format_group.add_argument(
        "--format",
        type=str,
        choices=[fmt.value for fmt in ResultFormat],
        default=os.environ.get("SPARQL_FORMAT", ResultFormat.JSON.value),
        help=f"Result format (default: {ResultFormat.JSON.value})"
    )
    format_group.add_argument(
        "--pretty-print",
        action="store_true",
        default=os.environ.get("SPARQL_PRETTY_PRINT", "false").lower() == "true",
        help="Pretty print JSON output (default: false)"
    )
    format_group.add_argument(
        "--include-metadata",
        type=lambda x: x.lower() == "true",
        default=os.environ.get("SPARQL_INCLUDE_METADATA", "true").lower() == "true",
        help="Include query metadata in results (default: true)"
    )
    
    return parser.parse_args()


def create_config_from_args(args: argparse.Namespace) -> SPARQLConfig:
    """Create a configuration object from command-line arguments.
    
    Args:
        args: The parsed command-line arguments.
        
    Returns:
        A SPARQLConfig object.
    """
    # Use environment variable if endpoint not provided in args
    endpoint_url = args.endpoint or os.environ.get("SPARQL_ENDPOINT")
    
    return SPARQLConfig(
        endpoint_url=endpoint_url,
        request_timeout=args.timeout,
        max_results=args.max_results,
        cache_enabled=args.cache_enabled,
        cache_ttl=args.cache_ttl,
        cache_max_size=args.cache_max_size,
        cache_strategy=CacheStrategy(args.cache_strategy),
        default_format=ResultFormat(args.format),
        pretty_print=args.pretty_print,
        include_metadata=args.include_metadata
    )


def run_server(config: SPARQLConfig, transport: str = "stdio", host: str = "localhost", port: int = 8000) -> None:
    """Run the MCP SPARQL Server with the given configuration.
    
    Args:
        config: The server configuration.
        transport: Transport type (stdio or http).
        host: Host to bind HTTP server to (only used for http transport).
        port: Port to bind HTTP server to (only used for http transport).
    """
    logger.info(f"Starting MCP SPARQL Server with endpoint: {config.endpoint_url}")
    
    # Initialize the SPARQL server with the configuration
    sparql_server = SPARQLServer(config)
    
    # Initialize content processor for Luxembourg legal documents
    content_processor = ContentProcessor()
    
    # Create the MCP server
    mcp = FastMCP("SPARQL Query Server")
    
    # Define the main query tool
    query_doc = f"""
    Execute a SPARQL query against the endpoint {config.endpoint_url}.
    
    Args:
        query_string: A valid SPARQL query string.
        format: Optional format for the results (json, simplified, or tabular).
                If not provided, the server's default format will be used.
    
    Returns:
        The query results in the specified format.
    """
    
    @mcp.tool(description=query_doc)
    def query(
        query_string: str, 
        format: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a SPARQL query and return the results.
        
        Args:
            query_string: The SPARQL query to execute.
            format: Optional result format.
            
        Returns:
            The query results.
        """
        logger.debug(f"Executing query: {query_string[:50]}...")
        
        # Convert format string to enum if provided
        format_type = None
        if format:
            try:
                format_type = ResultFormat(format)
            except ValueError:
                return {
                    "error": f"Invalid format: {format}. Must be one of: {', '.join([f.value for f in ResultFormat])}"
                }
                
        return sparql_server.query(query_string, format_type)
    
    # Add a tool for cache management
    cache_doc = """
    Manage the query cache.
    
    Args:
        action: The action to perform on the cache ("clear" or "stats").
    
    Returns:
        The result of the cache operation.
    """
    
    @mcp.tool(description=cache_doc)
    def cache(action: str) -> Dict[str, Any]:
        """Manage the query cache.
        
        Args:
            action: The cache action to perform.
            
        Returns:
            The result of the cache operation.
        """
        logger.debug(f"Cache action: {action}")
        
        if action.lower() == "clear":
            sparql_server.clear_cache()
            return {"status": "success", "message": "Cache cleared"}
        elif action.lower() == "stats":
            return {"status": "success", "stats": sparql_server.get_cache_stats()}
        else:
            return {
                "status": "error", 
                "message": f"Invalid cache action: {action}. Must be 'clear' or 'stats'."
            }
    
    # Luxembourg Legal Intelligence Tools
    
    @mcp.tool(description="Search Luxembourg legal documents with full content extraction")
    def search_luxembourg_documents(
        keywords: str,
        limit: int = 10,
        include_content: bool = True
    ) -> Dict[str, Any]:
        """Search Luxembourg legal documents and extract full content.
        
        Args:
            keywords: Search keywords (e.g., 'environmental protection', 'tax law')
            limit: Maximum number of results (default: 10)
            include_content: Whether to extract full document content (default: true)
            
        Returns:
            List of documents with metadata and full content
        """
        logger.info(f"Searching Luxembourg documents for: {keywords}")
        
        # Use exact SPARQL query as provided by user
        query = f"""
        PREFIX jolux: <http://data.legilux.public.lu/resource/ontology/jolux#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        
        SELECT DISTINCT ?entity ?date ?title ?docType
        WHERE {{
            ?entity jolux:dateDocument ?date ;
                    a ?docType ;
                    jolux:isRealizedBy ?expression .
            ?expression jolux:title ?title .
            FILTER(regex(str(?title), '{keywords}'^^xsd:string))
        }}
        ORDER BY DESC(?date)
        LIMIT {limit}
        """
        
        try:
            # Execute SPARQL query
            results = sparql_server.query(query, ResultFormat.SIMPLIFIED)
            
            # Handle SimplifiedFormatter results - results.results is a list of simplified objects
            search_results = results.get('results', [])
            if not search_results:
                return {"results": [], "message": "No documents found"}
            
            documents = []
            for result in search_results:
                doc = {
                    'uri': result.get('entity', ''),
                    'title': result.get('title', ''),
                    'date': result.get('date', ''),
                    'type': result.get('docType', ''),
                }
                
                # Extract full content if requested
                if include_content and doc['uri']:
                    content = content_processor.extract_entity_content(doc['uri'])
                    if content:
                        doc.update({
                            'content': content.get('text', ''),
                            'summary': content.get('summary', ''),
                            'document_type': content.get('document_type', ''),
                            'legal_concepts': content.get('legal_concepts', []),
                            'content_source': content.get('source_url', ''),
                            'content_type': content.get('content_type', '')
                        })
                
                documents.append(doc)
            
            return {
                "results": documents,
                "count": len(documents),
                "query_used": query
            }
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return {"error": f"Search failed: {str(e)}"}
    
    
    # Handle signals for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info(f"Server is ready to receive queries via {transport} transport")
    
    # Run the MCP server with the specified transport
    if transport == "streamable-http":
        logger.info(f"Starting streamable HTTP server on {host}:{port}")
        mcp.run(transport="streamable-http", host=host, port=port, path="/mcp")
    elif transport == "sse":
        logger.info(f"Starting SSE server on {host}:{port}")
        mcp.run(transport="sse", host=host, port=port)
    else:
        logger.info("Starting stdio transport")
        mcp.run(transport="stdio")


def main() -> None:
    """Run the MCP SPARQL Query Server as a regular process or daemon."""
    args = parse_args()
    
    # Create the configuration
    config = create_config_from_args(args)
    
    # If running as a daemon, set up logging to file
    if args.daemon:
        logger.info("Starting server in daemon mode")
        
        # Configure log file
        log_file = args.log_file
        if not log_file:
            log_file = "/var/log/mcp-sparql-server.log"
            logger.info(f"No log file specified, using default: {log_file}")
        
        # Configure PID file
        pid_file = args.pid_file
        if not pid_file:
            pid_file = "/var/run/mcp-sparql-server.pid"
            logger.info(f"No PID file specified, using default: {pid_file}")
        
        # Ensure directories exist
        log_dir = os.path.dirname(log_file)
        pid_dir = os.path.dirname(pid_file)
        
        os.makedirs(log_dir, exist_ok=True)
        os.makedirs(pid_dir, exist_ok=True)
        
        # Set up daemon context
        log_file_handle = open(log_file, 'a+')
        pid_file_handle = open(pid_file, 'w+')
        
        # Configure the daemon context
        context = daemon.DaemonContext(
            working_directory='/',
            umask=0o002,
            pidfile=pid_file_handle,
            stdout=log_file_handle,
            stderr=log_file_handle,
        )
        
        # Start the daemon
        with context:
            # Reconfigure logging for daemon mode
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)
                
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            root_logger.addHandler(file_handler)
            
            # Write PID to the file
            with open(pid_file, 'w') as f:
                f.write(str(os.getpid()))
                
            # Run the server
            run_server(config, args.transport, args.host, args.port)
    else:
        # Run in foreground mode
        run_server(config, args.transport, args.host, args.port)


if __name__ == "__main__":
    main()