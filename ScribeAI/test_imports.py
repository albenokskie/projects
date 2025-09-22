#!/usr/bin/env python3
"""Test script to check if Scribe imports work"""

try:
    print("Testing Scribe imports...")
    from scribe import Config, CodeAnalyzer, AIDocumentationGenerator, ConfluencePublisher
    print("✅ All imports successful!")
    
    print("Testing config loading...")
    config = Config("scribe_config.yaml")
    print("✅ Config loaded successfully!")
    print(f"Confluence URL: {config.confluence_url}")
    print(f"AI Model: {config.ai_model}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
