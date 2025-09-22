#!/usr/bin/env python3
"""
Atlassian Confluence Connection Tester
This script tests the connection to Confluence using email and API token.
"""

import requests  # For HTTP API calls - INSTALL WITH: pip install requests
from requests.auth import HTTPBasicAuth  # For HTTP Basic Authentication
import json  # Built-in Python library
import logging  # Built-in Python library
from typing import Tuple, Optional, Dict, Any  # Built-in Python library
from datetime import datetime  # Built-in Python library
import sys  # Built-in Python library

class ConfluenceConnectionTester:
    def __init__(self, base_url: str, username: str, api_token: str):
        """
        Initialize Confluence Connection Tester
        
        Args:
            base_url: Your Confluence base URL (e.g., 'https://your-domain.atlassian.net/wiki')
            username: Your email address
            api_token: Your API token from Atlassian account settings
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.api_token = api_token
        self.auth = HTTPBasicAuth(username, api_token)
        self.session = requests.Session()
        self.session.auth = self.auth
        self.logger = self._setup_logging()
        
        # Test results
        self.test_results = {
            'connection': False,
            'authentication': False,
            'permissions': False,
            'api_access': False,
            'user_info': None,
            'spaces_count': 0,
            'error_details': []
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger('ConfluenceConnectionTester')
        logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        return logger
    
    def test_basic_connection(self) -> bool:
        """Test basic network connectivity to Confluence"""
        self.logger.info("🔗 Testing basic connection...")
        
        try:
            # Simple GET request to the base URL
            response = requests.get(f"{self.base_url}/status", timeout=10)
            if response.status_code == 200:
                self.logger.info("✅ Basic connection successful")
                self.test_results['connection'] = True
                return True
            else:
                self.logger.error(f"❌ Connection failed - Status: {response.status_code}")
                self.test_results['error_details'].append(f"Connection status: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Connection failed - Error: {e}")
            self.test_results['error_details'].append(f"Connection error: {str(e)}")
            return False
    
    def test_authentication(self) -> bool:
        """Test API authentication"""
        self.logger.info("🔐 Testing authentication...")
        
        try:
            # Test authentication with user info endpoint
            url = f"{self.base_url}/rest/api/user/current"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                self.test_results['user_info'] = user_data
                display_name = user_data.get('displayName', 'Unknown')
                account_id = user_data.get('accountId', 'Unknown')
                
                self.logger.info(f"✅ Authentication successful")
                self.logger.info(f"   User: {display_name}")
                self.logger.info(f"   Account ID: {account_id}")
                self.logger.info(f"   Email: {self.username}")
                
                self.test_results['authentication'] = True
                return True
            elif response.status_code == 401:
                self.logger.error("❌ Authentication failed - Invalid credentials")
                self.test_results['error_details'].append("Invalid email or API token")
                return False
            elif response.status_code == 403:
                self.logger.error("❌ Authentication failed - Access forbidden")
                self.test_results['error_details'].append("Access forbidden - check permissions")
                return False
            else:
                self.logger.error(f"❌ Authentication failed - Status: {response.status_code}")
                self.test_results['error_details'].append(f"Auth status: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Authentication test failed - Error: {e}")
            self.test_results['error_details'].append(f"Auth error: {str(e)}")
            return False
    
    def test_api_access(self) -> bool:
        """Test API access permissions"""
        self.logger.info("🔑 Testing API access permissions...")
        
        try:
            # Test spaces endpoint
            url = f"{self.base_url}/rest/api/space"
            params = {'limit': 5}
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                spaces_data = response.json()
                spaces_count = len(spaces_data.get('results', []))
                total_spaces = spaces_data.get('size', 0)
                
                self.test_results['spaces_count'] = total_spaces
                self.test_results['api_access'] = True
                
                self.logger.info(f"✅ API access successful")
                self.logger.info(f"   Can access {total_spaces} spaces")
                
                if spaces_count > 0:
                    self.logger.info("   Available spaces:")
                    for space in spaces_data.get('results', [])[:3]:
                        space_name = space.get('name', 'Unknown')
                        space_key = space.get('key', 'Unknown')
                        self.logger.info(f"     - {space_name} ({space_key})")
                
                return True
            else:
                self.logger.error(f"❌ API access failed - Status: {response.status_code}")
                self.test_results['error_details'].append(f"API access status: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ API access test failed - Error: {e}")
            self.test_results['error_details'].append(f"API access error: {str(e)}")
            return False
    
    def test_content_permissions(self) -> bool:
        """Test content read permissions"""
        self.logger.info("📄 Testing content read permissions...")
        
        try:
            # Test content endpoint
            url = f"{self.base_url}/rest/api/content"
            params = {'limit': 1, 'type': 'page'}
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                content_data = response.json()
                results = content_data.get('results', [])
                
                if results:
                    page = results[0]
                    page_title = page.get('title', 'Unknown')
                    page_id = page.get('id', 'Unknown')
                    
                    self.logger.info(f"✅ Content access successful")
                    self.logger.info(f"   Can read pages (sample: '{page_title}' - ID: {page_id})")
                    self.test_results['permissions'] = True
                    return True
                else:
                    self.logger.warning("⚠️  Content access granted but no pages found")
                    self.test_results['permissions'] = True
                    return True
            else:
                self.logger.error(f"❌ Content access failed - Status: {response.status_code}")
                self.test_results['error_details'].append(f"Content access status: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Content access test failed - Error: {e}")
            self.test_results['error_details'].append(f"Content access error: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all connection tests"""
        self.logger.info("🚀 Starting Confluence Connection Tests")
        self.logger.info("=" * 50)
        
        # Test sequence
        tests = [
            ("Basic Connection", self.test_basic_connection),
            ("Authentication", self.test_authentication),
            ("API Access", self.test_api_access),
            ("Content Permissions", self.test_content_permissions)
        ]
        
        # Run tests in sequence, stop if critical test fails
        for test_name, test_func in tests:
            try:
                success = test_func()
                if not success and test_name in ["Basic Connection", "Authentication"]:
                    self.logger.error(f"❌ Critical test '{test_name}' failed. Stopping tests.")
                    break
            except Exception as e:
                self.logger.error(f"❌ Test '{test_name}' crashed: {e}")
                self.test_results['error_details'].append(f"{test_name} crashed: {str(e)}")
        
        # Print summary
        self._print_summary()
        return self.test_results
    
    def _print_summary(self):
        """Print test results summary"""
        self.logger.info("=" * 50)
        self.logger.info("📋 CONNECTION TEST SUMMARY")
        self.logger.info("=" * 50)
        
        # Overall status
        all_passed = all([
            self.test_results['connection'],
            self.test_results['authentication'],
            self.test_results['api_access'],
            self.test_results['permissions']
        ])
        
        if all_passed:
            self.logger.info("🎉 ALL TESTS PASSED! Your connection is working perfectly.")
        else:
            self.logger.error("❌ SOME TESTS FAILED. Check the details below.")
        
        # Detailed results
        status_icon = lambda x: "✅" if x else "❌"
        self.logger.info(f"{status_icon(self.test_results['connection'])} Basic Connection")
        self.logger.info(f"{status_icon(self.test_results['authentication'])} Authentication")
        self.logger.info(f"{status_icon(self.test_results['api_access'])} API Access")
        self.logger.info(f"{status_icon(self.test_results['permissions'])} Content Permissions")
        
        # Additional info
        if self.test_results['user_info']:
            user = self.test_results['user_info']
            self.logger.info(f"👤 Logged in as: {user.get('displayName', 'Unknown')}")
        
        if self.test_results['spaces_count'] > 0:
            self.logger.info(f"🏠 Accessible spaces: {self.test_results['spaces_count']}")
        
        # Error details
        if self.test_results['error_details']:
            self.logger.info("🔍 Error Details:")
            for error in self.test_results['error_details']:
                self.logger.error(f"   - {error}")
        
        self.logger.info("=" * 50)

def main():
    """Main function to run the connection test"""
    print("Atlassian Confluence Connection Tester")
    print("=" * 40)
    
    # Configuration - Update these values
    confluence_base_url = 'https://trendmicro.atlassian.net/wiki'
    username = 'alvin_atillo@trendmicro.com'
    api_token = 'ATATT3xFfGF0e4VpkZkXoVAQDp0yJr7LkQisAire_bJZ32lNWdQ0bWk8DblYUzVoU0SeAlCxxRPt8hV-mEttrk9aknTgBpBu6GJBSIc7tIBLB3KtCoAyddDouh4VTF2MSXxpSgp09uM8O4EY0EjJCWnjhj_OiNLYH_SCALyKNgX_S2XI9yrs0tE=40812803'
    
    # Check if default values are still in place
    if 'your-confluence-site' in confluence_base_url:
        print("❌ Please update the confluence_base_url in the script:")
        print("   - confluence_base_url: Your actual Confluence URL")
        print("   Example: 'https://trendmicro.atlassian.net/wiki'")
        print("   Example: 'https://yourcompany.atlassian.net/wiki'")
        sys.exit(1)
    
    # Run tests
    tester = ConfluenceConnectionTester(confluence_base_url, username, api_token)
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if all([results['connection'], results['authentication']]):
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure

if __name__ == "__main__":
    main()
