"""
Official Notion SDK Client Adapter for CSV2Notion Neo

This module provides a drop-in replacement for the existing NotionClientExtended,
using the official Notion SDK while maintaining full compatibility.
"""

from copy import deepcopy
from typing import Any, Dict, Optional

from csv2notion_neo.notion_client import NotionClient
from csv2notion_neo.notion_db import NotionDB
from csv2notion_neo.utils_exceptions import NotionError


class NotionClientExtended(NotionClient):
    """
    Extended official Notion client that maintains compatibility
    with the existing NotionClientExtended interface.
    """
    
    def __init__(
        self,
        integration_token: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        workspace: Optional[str] = None,
        **kwargs: Any,
    ):
        """
        Initialize the extended official client.
        
        Args:
            integration_token: Notion integration token
            options: Client options
            workspace: Workspace name
            **kwargs: Additional arguments
        """
        if integration_token is None:
            raise ValueError("integration_token is required")
            
        self.options = options or {}
        super().__init__(integration_token, workspace=workspace, **kwargs)
    
    def get_collection_as_db(
        self, collection_id: str, force_refresh: bool = False
    ) -> Optional[NotionDB]:
        """
        Get a collection/database as a NotionDB wrapper instance.
        
        Args:
            collection_id: Collection/database ID
            force_refresh: Whether to force refresh
            
        Returns:
            NotionDB instance or None
        """
        try:
            # Check if we can access the database using parent's get_collection
            db_info = super().get_collection(collection_id, force_refresh)
            if db_info:
                return NotionDB(self, collection_id)
            return None
        except Exception:
            return None
    
    def create_record(
        self, 
        table: str, 
        parent: Any, 
        type: Optional[str] = None,
        permissions: Optional[list] = None,
        schema: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """
        Create a record - maintains compatibility with existing code.
        
        Args:
            table: Record type ('block', 'collection', etc.)
            parent: Parent object
            type: Record type (for blocks)
            permissions: Permissions (for blocks)
            schema: Schema (for collections)
            **kwargs: Additional parameters
            
        Returns:
            Created record ID
        """
        try:
            if table == "block":
                # Create a page block
                if type == "collection_view_page":
                    # Create a page that will contain a database
                    response = self.client.pages.create(
                        parent={"type": "page_id", "page_id": parent} if isinstance(parent, str) else parent,
                        properties={"title": [{"text": {"content": "New Database"}}]},
                        **kwargs
                    )
                    return response["id"]
                else:
                    # Create a regular page
                    response = self.client.pages.create(
                        parent={"type": "page_id", "page_id": parent} if isinstance(parent, str) else parent,
                        **kwargs
                    )
                    return response["id"]
            elif table == "collection":
                # Create a database using initial_data_source (API 2025-09-03)
                # Properties go inside initial_data_source, not at top level
                if schema:
                    response = self.client.databases.create(
                        parent={"type": "page_id", "page_id": parent} if isinstance(parent, str) else parent,
                        title=[{"type": "text", "text": {"content": "New Database"}}],
                        initial_data_source={"properties": schema},
                        **kwargs
                    )
                    return response["id"]
                else:
                    raise NotionError("Schema required for collection creation")
            else:
                raise NotionError(f"Unsupported table type: {table}")
        except Exception as e:
            raise NotionError(f"Failed to create {table} record: {e}") from e
    
    def post(self, endpoint: str, data: Dict[str, Any]) -> Any:
        """
        Make a POST request - maintains compatibility with existing code.
        
        Args:
            endpoint: API endpoint
            data: Request data
            
        Returns:
            Response data
        """
        # Map common endpoints to official API calls
        if endpoint == "findUser":
            # Find user by email
            email = data.get("email")
            if not email:
                raise NotionError("Email required for user lookup")
            
            # Search for user in workspace
            users = self.client.users.list()
            for user in users.get("results", []):
                if user.get("person", {}).get("email") == email:
                    return {"value": {"value": {"id": user["id"]}}}
            
            return {"value": {"value": None}}
        
        # For other endpoints, we'll need to implement specific mappings
        raise NotionError(f"Endpoint {endpoint} not yet implemented in official API adapter")
    
    def get_block(self, notion_url: str, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get a block/page by URL - maintains compatibility with existing code.
        
        Args:
            notion_url: Notion URL or page ID
            force_refresh: Whether to force refresh (ignored in official API)
            
        Returns:
            Block/page data or None if not found
        """
        return super().get_block(notion_url, force_refresh)
    
    def get_collection(self, collection_id: str, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get a collection/database by ID - maintains compatibility.
        
        Args:
            collection_id: Database/collection ID
            force_refresh: Whether to force refresh (ignored in official API)
            
        Returns:
            Database data or None if not found
        """
        return super().get_collection(collection_id, force_refresh)


def get_notion_client(
    integration_token: str, 
    workspace: Optional[str] = None, 
    **options
) -> NotionClientExtended:
    """
    Factory function to create official Notion client - maintains compatibility.
    
    Args:
        integration_token: Notion integration token
        workspace: Workspace name (for compatibility)
        **options: Additional options
        
    Returns:
        NotionClientExtended instance
    """
    try:
        client = NotionClientExtended(
            integration_token=integration_token,
            workspace=workspace,
            **options
        )
        return client
    except Exception as e:
        raise NotionError(f"Failed to initialize Notion client: {e}") from e
