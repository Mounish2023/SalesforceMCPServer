#!/usr/bin/env python3
"""
Test script for Salesforce MCP Server

This script tests all the tools exposed by the MCP server to ensure they work correctly.
It can be run in two modes:
1. Unit tests: Test the Salesforce client directly
2. Integration tests: Test the MCP server via MCP protocol
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add parent directory to path to import client
sys.path.insert(0, str(Path(__file__).parent))
from client import SalesforceClient


class TestSalesforceClient:
    """Test suite for SalesforceClient"""
    
    def __init__(self):
        self.client = SalesforceClient(auto_auth=False)
        self.test_account_id = None
        
    def setup(self):
        """Setup test environment"""
        print("🔧 Setting up test environment...")
        
        # Check if credentials are configured
        if not all([
            os.environ.get("SALESFORCE_CLIENT_ID"),
            os.environ.get("SALESFORCE_CLIENT_SECRET")
        ]):
            print("❌ ERROR: Salesforce credentials not configured!")
            print("Please set the following environment variables:")
            print("  - SALESFORCE_CLIENT_ID")
            print("  - SALESFORCE_CLIENT_SECRET")
            print("  - SALESFORCE_INSTANCE_URL (optional)")
            return False
        
        # Authenticate
        try:
            print("🔐 Authenticating with Salesforce...")
            token_data = self.client.authenticate_client_credentials()
            print(f"✅ Authentication successful!")
            print(f"   Instance: {token_data.get('instance_url')}")
            return True
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return False
    
    def test_get_accounts(self):
        """Test retrieving accounts"""
        print("\n📋 Test: Get Accounts")
        try:
            accounts = self.client.get_accounts(limit=5)
            print(f"✅ Retrieved {len(accounts)} accounts")
            if accounts:
                print(f"   First account: {accounts[0].get('Name')} (ID: {accounts[0].get('Id')})")
                # Store for later tests
                self.test_account_id = accounts[0].get('Id')
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def test_get_account_by_id(self):
        """Test retrieving a specific account"""
        if not self.test_account_id:
            print("\n⏭️  Skipping test_get_account_by_id (no account ID available)")
            return True
        
        print(f"\n🔍 Test: Get Account by ID ({self.test_account_id})")
        try:
            account = self.client.get_account_by_id(self.test_account_id)
            print(f"✅ Retrieved account: {account.get('Name')}")
            print(f"   Type: {account.get('Type')}")
            print(f"   Industry: {account.get('Industry')}")
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def test_search_accounts(self):
        """Test searching for accounts"""
        print("\n🔎 Test: Search Accounts")
        try:
            # Search for a common term
            results = self.client.search_accounts("Inc", limit=5)
            print(f"✅ Found {len(results)} accounts matching 'Inc'")
            if results:
                print(f"   First result: {results[0].get('Name')}")
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def test_create_and_delete_account(self):
        """Test creating and deleting an account"""
        print("\n➕ Test: Create Account")
        test_account_data = {
            "Name": "Test MCP Account - DELETE ME",
            "Type": "Prospect",
            "Industry": "Technology",
            "Phone": "555-0123",
            "Website": "https://test-mcp.example.com",
            "BillingCity": "San Francisco",
            "BillingState": "CA",
            "BillingCountry": "USA"
        }
        
        created_account_id = None
        try:
            created_account_id = self.client.create_account(test_account_data)
            print(f"✅ Created test account: {created_account_id}")
        except Exception as e:
            print(f"❌ Create failed: {e}")
            return False
        
        # Test update
        print("\n✏️  Test: Update Account")
        try:
            update_data = {
                "Phone": "555-9999",
                "Description": "Updated by MCP test script"
            }
            self.client.update_account(created_account_id, update_data)
            print(f"✅ Updated account {created_account_id}")
        except Exception as e:
            print(f"❌ Update failed: {e}")
        
        # Clean up - delete the test account
        print("\n🗑️  Test: Delete Account")
        try:
            self.client.delete_account(created_account_id)
            print(f"✅ Deleted test account {created_account_id}")
            return True
        except Exception as e:
            print(f"❌ Delete failed: {e}")
            return False
    
    def test_get_related_records(self):
        """Test getting opportunities and contacts"""
        if not self.test_account_id:
            print("\n⏭️  Skipping test_get_related_records (no account ID available)")
            return True
        
        print(f"\n📊 Test: Get Account Opportunities ({self.test_account_id})")
        try:
            opportunities = self.client.get_account_opportunities(self.test_account_id, limit=5)
            print(f"✅ Retrieved {len(opportunities)} opportunities")
            if opportunities:
                print(f"   First opportunity: {opportunities[0].get('Name')}")
        except Exception as e:
            print(f"❌ Failed: {e}")
        
        print(f"\n👥 Test: Get Account Contacts ({self.test_account_id})")
        try:
            contacts = self.client.get_account_contacts(self.test_account_id, limit=5)
            print(f"✅ Retrieved {len(contacts)} contacts")
            if contacts:
                print(f"   First contact: {contacts[0].get('Name')}")
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("=" * 70)
        print("🧪 SALESFORCE MCP SERVER TEST SUITE")
        print("=" * 70)
        
        if not self.setup():
            print("\n❌ Setup failed. Aborting tests.")
            return False
        
        tests = [
            ("Get Accounts", self.test_get_accounts),
            ("Get Account by ID", self.test_get_account_by_id),
            ("Search Accounts", self.test_search_accounts),
            ("Create/Update/Delete Account", self.test_create_and_delete_account),
            ("Get Related Records", self.test_get_related_records),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"\n❌ Test '{test_name}' crashed: {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} - {test_name}")
        
        print(f"\n  Total: {passed}/{total} tests passed")
        print("=" * 70)
        
        return passed == total


async def test_mcp_server_integration():
    """Test the MCP server via the MCP protocol"""
    print("\n" + "=" * 70)
    print("🌐 MCP SERVER INTEGRATION TEST")
    print("=" * 70)
    print("\n⚠️  This test requires the MCP server to be running separately.")
    print("Start the server with: python src/main.py")
    print("\n📝 Note: Full integration testing with MCP client is a future enhancement.")
    print("=" * 70)


def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Salesforce MCP Server")
    parser.add_argument(
        "--mode",
        choices=["unit", "integration", "all"],
        default="unit",
        help="Test mode: unit (client only), integration (MCP protocol), or all"
    )
    args = parser.parse_args()
    
    # Load environment variables if .env file exists
    env_file = Path(__file__).parent / "config" / ".env"
    if env_file.exists():
        print(f"📁 Loading environment from {env_file}")
        from dotenv import load_dotenv
        load_dotenv(env_file)
    
    success = True
    
    if args.mode in ("unit", "all"):
        tester = TestSalesforceClient()
        success = tester.run_all_tests() and success
    
    if args.mode in ("integration", "all"):
        asyncio.run(test_mcp_server_integration())
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
