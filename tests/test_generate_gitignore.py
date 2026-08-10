#!/usr/bin/env python3
"""
Test for the generate gitignore command
"""

import json
import sys
import os

# Add the path to the installed server
sys.path.insert(0, os.path.expanduser('~/.cursor/tools'))

def test_generate_gitignore():
    """The generate gitignore command"""
    
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
    
    try:
        # Import the request handler
        from how_to_do import handle_request
        
        # Handle the request
        response = handle_request(request)
        
        # Check the result
        assert "result" in response, f"generate gitignore failed: {response.get('error', {})}"
        
        print("✅ generate gitignore works correctly")
        print(f"Status: {response.get('result', {}).get('content', [{}])[0].get('text', '')[:200]}...")
            
    except Exception as e:
        assert False, f"Exception while running the command: {e}"

def test_load_gitignore_rules():
    """Loading gitignore rules"""
    
    try:
        from how_to_do import load_gitignore_rules
        
        rules = load_gitignore_rules()
        print(f"✅ Gitignore rules loaded: {len(rules)} categories")
        
        for category, patterns in rules.items():
            print(f"  - {category}: {len(patterns)} rules")
        
    except Exception as e:
        assert False, f"Failed to load gitignore rules: {e}"

def test_analyze_project():
    """Project analysis"""
    
    try:
        from how_to_do import analyze_project_for_gitignore, get_project_path
        
        project_path = get_project_path()
        print(f"📁 Analysing project: {project_path}")
        
        rules_by_category = analyze_project_for_gitignore(project_path)
        print(f"✅ Project analysed: {len(rules_by_category)} categories")
        
        for category, rules in rules_by_category.items():
            print(f"  - {category}: {len(rules)} rules")
        
    except Exception as e:
        assert False, f"Project analysis failed: {e}"

if __name__ == '__main__':
    print("🧪 Testing the generate gitignore command...")
    print()
    
    # Test 1: loading the rules
    print("1. Loading gitignore rules:")
    test1 = test_load_gitignore_rules()
    print()
    
    # Test 2: project analysis
    print("2. Project analysis:")
    test2 = test_analyze_project()
    print()
    
    # Test 3: the generate gitignore command
    print("3. The generate gitignore command:")
    test3 = test_generate_gitignore()
    print()
    
    # Final result
    if test1 and test2 and test3:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed") 