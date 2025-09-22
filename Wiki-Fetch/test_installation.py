#!/usr/bin/env python3
"""
Quick test script to verify the installation and basic functionality.
This script tests the imports and basic configuration without making API calls.
"""

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from wiki_fetch import ConfluenceAPI
        from config import ConfluenceConfig, ConfluenceConfigError
        from confluence_types import ConfluencePage, ConfluenceSearchResult
        print("[OK] All imports successful")
        return True
    except ImportError as e:
        print(f"[FAIL] Import failed: {e}")
        return False


def test_config_validation():
    """Test configuration validation."""
    print("Testing configuration validation...")
    
    try:
        from config import ConfluenceConfig, ConfluenceConfigError
        
        # Test missing configuration
        try:
            ConfluenceConfig(load_from_env=False)
            print("[FAIL] Should have failed with missing config")
            return False
        except ConfluenceConfigError:
            print("[OK] Correctly validates missing configuration")
        
        # Test valid configuration
        try:
            config = ConfluenceConfig(
                base_url="https://test.atlassian.net/wiki",
                username="test@example.com",
                api_token="test-token",
                load_from_env=False
            )
            print("[OK] Valid configuration accepted")
            
            # Test masking
            masked = config.mask_sensitive_data()
            if "test-tok..." in masked['api_token']:
                print("[OK] Sensitive data masking works")
            else:
                print("[FAIL] Sensitive data masking failed")
                return False
                
        except Exception as e:
            print(f"[FAIL] Valid configuration rejected: {e}")
            return False
            
        return True
        
    except Exception as e:
        print(f"[FAIL] Configuration test failed: {e}")
        return False


def test_api_initialization():
    """Test API client initialization."""
    print("Testing API client initialization...")
    
    try:
        from wiki_fetch import ConfluenceAPI
        from config import ConfluenceConfig
        
        # Test with explicit config
        config = ConfluenceConfig(
            base_url="https://test.atlassian.net/wiki",
            username="test@example.com",
            api_token="test-token",
            load_from_env=False
        )
        
        api = ConfluenceAPI(config=config)
        
        if api.base_url == "https://test.atlassian.net/wiki":
            print("[OK] API client initialized correctly")
            return True
        else:
            print("[FAIL] API client initialization failed")
            return False
            
    except Exception as e:
        print(f"[FAIL] API initialization test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("Confluence API Client - Installation Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config_validation,
        test_api_initialization
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("[SUCCESS] All tests passed! The installation is working correctly.")
        print("\nNext steps:")
        print("1. Copy .env.example to .env")
        print("2. Fill in your Confluence credentials")
        print("3. Run: python wiki_fetch.py")
    else:
        print("[ERROR] Some tests failed. Please check the error messages above.")
    
    print("=" * 50)


if __name__ == "__main__":
    main()