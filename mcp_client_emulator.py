#!/usr/bin/env python3
"""
MCP Client Emulator for testing the SPARQL server.

This is a minimal implementation that follows the MCP protocol
to communicate with the SPARQL server.
"""

import json
import subprocess
import time
import sys
import os
import signal
from typing import Dict, Any, Optional

class MCPClientEmulator:
    """A minimal MCP client emulator for testing."""
    
    def __init__(self, server_command, server_args=None, server_env=None):
        """Initialize the MCP client emulator.
        
        Args:
            server_command: The command to start the server.
            server_args: Optional arguments for the server command.
            server_env: Optional environment variables for the server.
        """
        self.server_command = server_command
        self.server_args = server_args or []
        self.server_env = server_env or {}
        self.server_process = None
        self.request_id = 0
    
    def start_server(self):
        """Start the MCP server."""
        cmd = [self.server_command] + self.server_args
        print(f"Starting MCP server: {' '.join(cmd)}")
        
        # Prepare environment
        env = os.environ.copy()
        env.update(self.server_env)
        
        # Start the server process
        self.server_process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        
        # Wait for server to start
        time.sleep(2)
        
        # Check if the server started successfully
        if self.server_process.poll() is not None:
            stderr = self.server_process.stderr.read()
            raise RuntimeError(f"Server failed to start: {stderr}")
        
        # Print any initial server output
        stderr_line = self.server_process.stderr.readline()
        while stderr_line and stderr_line.strip():
            print(f"Server: {stderr_line.strip()}")
            stderr_line = self.server_process.stderr.readline()
        
        print("Server started successfully")
    
    def stop_server(self):
        """Stop the MCP server."""
        if self.server_process:
            print("Stopping server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("Server didn't terminate gracefully, killing...")
                self.server_process.kill()
    
    def send_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request to the MCP server.
        
        Args:
            method: The method to call.
            params: The parameters for the method.
            
        Returns:
            The server's response.
        """
        if not self.server_process:
            raise RuntimeError("Server not started")
        
        # Increment request ID
        self.request_id += 1
        
        # Create the request message
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": self.request_id
        }
        
        # Send the request
        request_json = json.dumps(request)
        print(f"\nSending request: {request_json}")
        self.server_process.stdin.write(request_json + "\n")
        self.server_process.stdin.flush()
        
        # Read the response
        response_json = self.server_process.stdout.readline().strip()
        print(f"Raw response: {response_json}")
        
        if not response_json:
            return {"error": "No response from server"}
        
        try:
            response = json.loads(response_json)
            return response
        except json.JSONDecodeError:
            return {"error": f"Invalid JSON response: {response_json}"}
    
    def __enter__(self):
        """Start the server when entering a context."""
        self.start_server()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop the server when exiting a context."""
        self.stop_server()


def main():
    """Run the MCP client emulator."""
    # Server command and arguments
    server_command = "python"
    server_args = [
        "server.py",
        "--endpoint", 
        "https://data.legilux.public.lu/sparqlendpoint",
        "--format",
        "simplified"
    ]
    
    # Create the client emulator
    with MCPClientEmulator(server_command, server_args) as client:
        # Test a simple SPARQL query
        print("\n=== Testing SPARQL Query ===")
        query_result = client.send_request("query", {
            "query_string": "SELECT * WHERE { ?s ?p ?o } LIMIT 2",
            "format": "simplified"
        })
        
        # Print the formatted result
        if "result" in query_result:
            print("\nQuery Result:")
            print(json.dumps(query_result["result"], indent=2))
        else:
            print("\nFull Response:")
            print(json.dumps(query_result, indent=2))
        
        # Test the cache stats
        print("\n=== Testing Cache Stats ===")
        cache_result = client.send_request("cache", {
            "action": "stats"
        })
        
        # Print the formatted result
        if "result" in cache_result:
            print("\nCache Stats:")
            print(json.dumps(cache_result["result"], indent=2))
        else:
            print("\nFull Response:")
            print(json.dumps(cache_result, indent=2))
        
        print("\nTests completed successfully")


if __name__ == "__main__":
    main()