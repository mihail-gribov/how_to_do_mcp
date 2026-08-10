#!/usr/bin/env python3
"""
Cursor IDE integration test
"""

import json
import sys
import os

def test_mcp_configuration():
    """MCP configuration"""
    
    mcp_config_path = os.path.expanduser('~/.cursor/mcp.json')
    
    assert os.path.exists(mcp_config_path), "MCP configuration not found"
    
    try:
        with open(mcp_config_path, 'r') as f:
            config = json.load(f)
        
        # The HOW TO DO server must be configured
        servers = config.get('mcpServers', {})
        how_to_do_server = None
        
        for server_name, server_config in servers.items():
            if 'how_to_do' in server_name.lower():
                how_to_do_server = server_config
                break
        
        assert how_to_do_server is not None, "HOW TO DO server not found in the MCP configuration"
        
        print("✅ HOW TO DO server found in the MCP configuration")
        print(f"   Name: {list(servers.keys())[list(servers.values()).index(how_to_do_server)]}")
        print(f"   Command: {how_to_do_server.get('command', 'N/A')}")
            
    except Exception as e:
        assert False, f"Failed to read the MCP configuration: {e}"

def test_server_files():
    """Server files"""
    
    server_dir = os.path.expanduser('~/.cursor/tools')
    required_files = ['how_to_do.py', 'how_to_do.json', 'how_to_do_gitignore.toml']
    
    print("📁 Checking server files:")
    
    for file in required_files:
        file_path = os.path.join(server_dir, file)
        assert os.path.exists(file_path), f"File {file} not found"
        size = os.path.getsize(file_path)
        print(f"   ✅ {file} ({size} bytes)")

def test_server_executable():
    """The server is executable"""
    
    server_path = os.path.expanduser('~/.cursor/tools/how_to_do.py')
    
    assert os.path.exists(server_path), "Server not found"
    assert os.access(server_path, os.X_OK), "Server is not executable"
    
    print("✅ Server is executable")

def test_generate_gitignore_command():
    """The generate gitignore command"""
    
    try:
        # Import the server
        sys.path.insert(0, os.path.expanduser('~/.cursor/tools'))
        from how_to_do import handle_request
        
        # Create a test request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "generate_gitignore",
                "arguments": {}
            }
        }
        
        # Handle the request
        response = handle_request(request)
        
        assert "result" in response, f"generate gitignore failed: {response.get('error', {})}"
        
        content = response["result"]["content"][0]["text"]
        
        # The response must contain rules
        assert "RULES FOR USE" in content and "##" in content, "generate gitignore returned an unexpected response"
        
        print("✅ generate gitignore returns a valid response")
        print(f"   Response length: {len(content)} characters")
            
    except Exception as e:
        assert False, f"Command test failed: {e}"

if __name__ == '__main__':
    print("🧪 Testing Cursor IDE integration...")
    print()
    
    # Test 1: MCP configuration
    print("1. MCP configuration:")
    test1 = test_mcp_configuration()
    print()
    
    # Test 2: server files
    print("2. Server files:")
    test2 = test_server_files()
    print()
    
    # Test 3: the server is executable
    print("3. Server is executable:")
    test3 = test_server_executable()
    print()
    
    # Test 4: the generate gitignore command
    print("4. The generate gitignore command:")
    test4 = test_generate_gitignore_command()
    print()
    
    # Final result
    if test1 and test2 and test3 and test4:
        print("🎉 All tests passed!")
        print()
        print("📋 How to use it in Cursor:")
        print("1. Restart Cursor IDE")
        print("2. Open the AI chat")
        print("3. Run the command: generate gitignore")
        print("4. The server analyses the project and writes .gitignore")
    else:
        print("❌ Some tests failed")
        print("   Check the installation and restart Cursor IDE") 