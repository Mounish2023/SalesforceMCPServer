#!/usr/bin/env python3
# ==============================================================================
#                  Salesforce MCP Server - Implementation
# ==============================================================================

"""A Salesforce MCP server with account management tools.

This server demonstrates:
- Account retrieval and search
- Account CRUD operations
- Related records (contacts, opportunities)
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from openmcp import MCPServer, tool

# Import from parent directory
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from client import SalesforceClient

# Suppress logs for clean output
for logger_name in ("mcp", "httpx", "uvicorn", "uvicorn.access", "uvicorn.error"):
    logging.getLogger(logger_name).setLevel(logging.CRITICAL)

server = MCPServer("salesforce-mcp-server")

# Initialize Salesforce client (will use client_credentials authentication)
sf_client = None


def get_client() -> SalesforceClient:
    """Get or create the Salesforce client instance"""
    global sf_client
    if sf_client is None:
        sf_client = SalesforceClient(auto_auth=True)
    return sf_client


with server.binding():

    @tool(description="Retrieve a list of Salesforce accounts")
    def get_accounts(limit: int = 10, fields: list[str] | None = None) -> list[dict[str, Any]]:
        """Returns account details including ID, Name, Type, Industry, Phone, Website, and billing information.
        
        Args:
            limit: Maximum number of accounts to retrieve (default: 10)
            fields: Optional list of fields to retrieve
        """
        client = get_client()
        return client.get_accounts(limit=limit, fields=fields)

    @tool(description="Retrieve a specific Salesforce account by its ID")
    def get_account_by_id(account_id: str, fields: list[str] | None = None) -> dict[str, Any]:
        """Returns detailed account information.
        
        Args:
            account_id: Salesforce Account ID (18-character ID)
            fields: Optional list of fields to retrieve
        """
        client = get_client()
        return client.get_account_by_id(account_id, fields=fields)

    @tool(description="Search for Salesforce accounts by name or other fields")
    def search_accounts(search_term: str, limit: int = 10) -> list[dict[str, Any]]:
        """Uses SOSL (Salesforce Object Search Language) to find matching accounts.
        
        Args:
            search_term: Search term to look for in account fields
            limit: Maximum number of results to return (default: 10)
        """
        client = get_client()
        return client.search_accounts(search_term, limit=limit)

    @tool(description="Create a new Salesforce account")
    def create_account(account_data: dict[str, Any]) -> str:
        """Returns the ID of the created account.
        
        Args:
            account_data: Account data as key-value pairs. 
                         Common fields: Name (required), Type, Industry, Phone, Website,
                         BillingStreet, BillingCity, BillingState, BillingPostalCode, BillingCountry
        """
        client = get_client()
        return client.create_account(account_data)

    @tool(description="Update an existing Salesforce account")
    def update_account(account_id: str, account_data: dict[str, Any]) -> bool:
        """Returns true if successful.
        
        Args:
            account_id: Salesforce Account ID to update
            account_data: Account fields to update as key-value pairs
        """
        client = get_client()
        client.update_account(account_id, account_data)
        return True

    @tool(description="Delete a Salesforce account by ID")
    def delete_account(account_id: str) -> bool:
        """Returns true if successful. Use with caution!
        
        Args:
            account_id: Salesforce Account ID to delete
        """
        client = get_client()
        client.delete_account(account_id)
        return True

    @tool(description="Get opportunities associated with a Salesforce account")
    def get_account_opportunities(account_id: str, limit: int = 10) -> list[dict[str, Any]]:
        """Returns opportunity details including stage, amount, and close date.
        
        Args:
            account_id: Salesforce Account ID
            limit: Maximum number of opportunities to retrieve (default: 10)
        """
        client = get_client()
        return client.get_account_opportunities(account_id, limit=limit)

    @tool(description="Get contacts associated with a Salesforce account")
    def get_account_contacts(account_id: str, limit: int = 10) -> list[dict[str, Any]]:
        """Returns contact details including name, email, phone, and title.
        
        Args:
            account_id: Salesforce Account ID
            limit: Maximum number of contacts to retrieve (default: 10)
        """
        client = get_client()
        return client.get_account_contacts(account_id, limit=limit)


async def main() -> None:
    """Start the MCP server on streamable-http transport."""
    print("🚀 Starting Salesforce MCP Server...")
    print("📡 Transport: streamable-http")
    print("🔧 Available tools: get_accounts, get_account_by_id, search_accounts, create_account,")
    print("                   update_account, delete_account, get_account_opportunities, get_account_contacts")
    print()
    
    # Initialize the client on startup
    try:
        get_client()
        print("✅ Salesforce client initialized successfully")
    except Exception as e:
        print(f"⚠️  Warning: Failed to initialize Salesforce client: {e}")
        print("   Server will start but tools may fail until client is configured properly")
    
    print()
    await server.serve(transport="streamable-http", verbose=False, log_level="critical")


if __name__ == "__main__":
    asyncio.run(main())
