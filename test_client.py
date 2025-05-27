#!/usr/bin/env python3
"""
Simple MCP test client for the SPARQL server.

This client communicates with the MCP SPARQL server using the
Message Carrying Protocol over stdio.
"""

import json
import sys
import subprocess
import time
import os
import signal
import argparse
from typing import Dict, Any, List, Optional

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Simple MCP test client for SPARQL server")
    parser.add_argument(
        "--server-path", 
        default="./server.py",
        help="Path to the server.py file"
    )
    parser.add_argument(
        "--endpoint", 
        default="https://data.legilux.public.lu/sparqlendpoint",
        help="SPARQL endpoint URL"
    )
    parser.add_argument(
        "--format", 
        default="simplified",
        choices=["json", "simplified", "tabular"],
        help="Result format"
    )
    parser.add_argument(
        "--query", 
        default="SELECT * WHERE { ?s ?p ?o } LIMIT 3",
        help="SPARQL query to execute"
    )
    parser.add_argument(
        "--config-file",
        help="Path to MCP server configuration JSON file"
    )
    return parser.parse_args()

def read_json_message(stream) -> Dict[str, Any]:
    """Read a JSON message from a stream."""
    line = stream.readline().strip()
    if not line:
        return {}
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        print(f"Error decoding JSON: {line}")
        return {}

def start_server_from_args(args) -> subprocess.Popen:
    """Start the server using command-line arguments."""
    cmd = [
        "python", 
        args.server_path, 
        "--endpoint", 
        args.endpoint,
        "--format", 
        args.format
    ]
    print(f"Starting server with command: {' '.join(cmd)}")
    
    return subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1  # Line buffered
    )

def start_server_from_config(config_path: str) -> subprocess.Popen:
    """Start the server using an MCP configuration file."""
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Get the first server config (or the default one if specified)
    server_name = config.get("defaultServer")
    server_config = None
    
    if server_name:
        for server in config.get("mcpServers", []):
            if server.get("name") == server_name:
                server_config = server
                break
    
    if not server_config and config.get("mcpServers"):
        server_config = config["mcpServers"][0]
    
    if not server_config:
        raise ValueError("No server configuration found in config file")
    
    # Prepare the command and environment
    cmd = [server_config["command"]] + server_config.get("args", [])
    env = os.environ.copy()
    env.update(server_config.get("env", {}))
    
    print(f"Starting server with command: {' '.join(cmd)}")
    
    return subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,  # Line buffered
        env=env
    )

def main():
    """Run the MCP test client."""
    args = parse_args()
    
    # Start the server
    if args.config_file:
        server_process = start_server_from_config(args.config_file)
    else:
        server_process = start_server_from_args(args)
    
    # Set up signal handler for graceful shutdown
    def signal_handler(signum, frame):
        print(f"\nReceived signal {signum}, shutting down...")
        server_process.terminate()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(2)
    
    # Check if the server is running
    if server_process.poll() is not None:
        print("Server failed to start. Error output:")
        print(server_process.stderr.read())
        sys.exit(1)
    
    # Log any server output
    server_stderr = ""
    while server_process.stderr.readable() and not server_process.stderr.closed:
        line = server_process.stderr.readline()
        if not line:
            break
        server_stderr += line
    
    if server_stderr:
        print("Server output:")
        print(server_stderr)
    
    try:
        # Send a query
        query_request = {
            "name": "query",
            "args": {
                "query_string": args.query,
                "format": args.format
            }
        }
        
        print(f"\nSending query: {args.query}")
        server_process.stdin.write(json.dumps(query_request) + "\n")
        server_process.stdin.flush()
        
        # Read response
        print("Waiting for response...")
        response = read_json_message(server_process.stdout)
        
        if response:
            print("\nQuery results:")
            print(json.dumps(response, indent=2))
            
            # Get result count if available
            if "results" in response and isinstance(response["results"], list):
                print(f"\nFound {len(response['results'])} results")
            elif "rows" in response and isinstance(response["rows"], list):
                print(f"\nFound {len(response['rows'])} results")
        else:
            print("No response received")
        
        # Query cache stats
        print("\nQuerying cache statistics...")
        cache_request = {
            "name": "cache",
            "args": {
                "action": "stats"
            }
        }
        
        server_process.stdin.write(json.dumps(cache_request) + "\n")
        server_process.stdin.flush()
        
        # Read cache stats response
        cache_response = read_json_message(server_process.stdout)
        
        if cache_response:
            print("\nCache statistics:")
            print(json.dumps(cache_response, indent=2))
        else:
            print("No cache statistics received")
    
    finally:
        # Terminate the server
        print("\nShutting down server...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()

if __name__ == "__main__":
    main()