"""
Official Notion SDK Client Adapter for CSV2Notion Neo

This module provides a compatibility layer between the existing CSV2Notion Neo
codebase and the official Notion SDK, ensuring seamless migration without
breaking existing functionality.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from notion_client import Client, APIResponseError, APIErrorCode
from notion_client.helpers import get_id

from csv2notion_neo.utils_exceptions import NotionError, CriticalError


class NotionClientOfficial:
    """
    Official Notion SDK client adapter that maintains compatibility
    with the existing CSV2Notion Neo codebase.
    """
    
    def __init__(self, integration_token: str, workspace: Optional[str] = None, **options):
        """
        Initialize the official Notion client.
        
        Args:
            integration_token: Notion integration token (replaces token_v2)
            workspace: Workspace name (for compatibility, not used in official API)
            **options: Additional client options
        """
        self.integration_token = integration_token
        self.workspace = workspace
        self.options = options
        
        # Initialize official Notion client
        self.client = Client(auth=integration_token)
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Cache for performance
        self._cache_users: Dict[str, Dict[str, Any]] = {}
        self._cache_databases: Dict[str, Dict[str, Any]] = {}
        
    def get_block(self, notion_url: str, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get a block/page by URL - maintains compatibility with existing code.
        
        Args:
            notion_url: Notion URL or page ID
            force_refresh: Whether to force refresh (ignored in official API)
            
        Returns:
            Block/page data or None if not found
        """
        try:
            # Extract page ID from URL if needed
            page_id = get_id(notion_url) if notion_url.startswith('http') else notion_url
            
            # Try to get as page first
            try:
                return self.client.pages.retrieve(page_id=page_id)
            except APIResponseError as e:
                if e.code == APIErrorCode.ObjectNotFound:
                    # Try as database
                    try:
                        return self.client.databases.retrieve(database_id=page_id)
                    except APIResponseError:
                        return None
                raise NotionError(f"Cannot access {notion_url}") from e
                
        except Exception as e:
            self.logger.error(f"Error getting block {notion_url}: {e}")
            raise NotionError(f"Error accessing {notion_url}") from e
    
    def get_collection(self, collection_id: str, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get a database/collection by ID - maintains compatibility.
        
        Args:
            collection_id: Database/collection ID
            force_refresh: Whether to force refresh (ignored in official API)
            
        Returns:
            Database data or None if not found
        """
        try:
            return self.client.databases.retrieve(database_id=collection_id)
        except APIResponseError as e:
            if e.code == APIErrorCode.ObjectNotFound:
                return None
            raise NotionError(f"Cannot access database {collection_id}") from e
    
    def create_record(self, table: str, parent: Any, **kwargs) -> str:
        """
        Create a record - maintains compatibility with existing code.
        
        Args:
            table: Record type ('block', 'collection', etc.)
            parent: Parent object
            **kwargs: Additional parameters
            
        Returns:
            Created record ID
        """
        try:
            if table == "block":
                # Create a page block
                response = self.client.pages.create(
                    parent={"type": "page_id", "page_id": parent} if isinstance(parent, str) else parent,
                    **kwargs
                )
                return response["id"]
            elif table == "collection":
                # Create a database
                response = self.client.databases.create(**kwargs)
                return response["id"]
            else:
                raise NotionError(f"Unsupported table type: {table}")
        except APIResponseError as e:
            raise NotionError(f"Failed to create {table} record") from e
    
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
    
    @property
    def current_user(self) -> Dict[str, Any]:
        """
        Get current user information - maintains compatibility.
        
        Returns:
            Current user data
        """
        try:
            # Get bot user (integration user)
            users = self.client.users.list()
            for user in users.get("results", []):
                if user.get("type") == "bot":
                    return {
                        "id": user["id"],
                        "name": user.get("name", "Integration"),
                        "email": user.get("person", {}).get("email", ""),
                        "avatar_url": user.get("avatar_url", "")
                    }
            
            # Fallback to first user if no bot found
            if users.get("results"):
                user = users["results"][0]
                return {
                    "id": user["id"],
                    "name": user.get("name", "User"),
                    "email": user.get("person", {}).get("email", ""),
                    "avatar_url": user.get("avatar_url", "")
                }
            
            raise NotionError("No user found")
            
        except APIResponseError as e:
            raise NotionError("Failed to get current user") from e
    
    @property
    def current_space(self) -> Dict[str, Any]:
        """
        Get current workspace/space information - maintains compatibility.
        
        Returns:
            Workspace data
        """
        # In the official API, workspace info is not directly available
        # We'll return a minimal structure for compatibility
        return {
            "id": "workspace",
            "name": self.workspace or "Workspace",
            "users": self._get_workspace_users()
        }
    
    def _get_workspace_users(self) -> List[Dict[str, Any]]:
        """
        Get workspace users.
        
        Returns:
            List of user data
        """
        try:
            users = self.client.users.list()
            return users.get("results", [])
        except APIResponseError as e:
            self.logger.warning(f"Failed to get workspace users: {e}")
            return []
    
    def upload_file(self, file_path: Path, parent_block_id: str) -> Tuple[str, Dict[str, Any]]:
        """
        Upload a file using the official API with retry logic.
        
        Args:
            file_path: Path to file to upload
            parent_block_id: Parent block ID
            
        Returns:
            Tuple of (file_url, metadata)
        """
        import time
        import random
        from requests.exceptions import Timeout, ConnectionError
        from notion_client.errors import APIResponseError
        
        max_retries = 5
        base_delay = 2.0
        
        for attempt in range(max_retries + 1):
            try:
                # Check file size (20MB limit for single part upload)
                file_size = file_path.stat().st_size
                if file_size > 20 * 1024 * 1024:  # 20MB
                    raise NotionError(f"File size {file_size} exceeds 20MB limit")
                
                # Create file upload
                response = self.client.file_uploads.create(
                    mode="single_part",
                    filename=file_path.name,
                    content_type=self._get_content_type(file_path)
                )
                file_upload_id = response["id"]
                
                # Upload file
                with open(file_path, "rb") as f:
                    upload_response = self.client.file_uploads.send(
                        file_upload_id=file_upload_id,
                        file=f
                    )
                
                if upload_response.get("status") != "uploaded":
                    raise NotionError(f"File upload failed with status: {upload_response.get('status')}")
                
                # Return file URL and metadata
                file_url = f"attachment:{file_upload_id}:{file_path.name}"
                metadata = {
                    "source": [[file_url]],
                    "type": "file",
                    "file_id": file_upload_id
                }
                
                return file_url, metadata
                
            except (APIResponseError, Timeout, ConnectionError) as e:
                # Check if this is a retryable error
                if attempt < max_retries:
                    # Calculate exponential backoff with jitter
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    
                    # Check for specific error codes that should be retried
                    if hasattr(e, 'status_code'):
                        if e.status_code in [503, 504, 429]:  # Service unavailable, Gateway timeout, Rate limited
                            self.logger.warning(f"Retryable error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                            time.sleep(delay)
                            continue
                        elif e.status_code in [400, 401, 403, 404]:  # Client errors - don't retry
                            raise NotionError(f"Failed to upload file {file_path}: {e}") from e
                    
                    # For timeout and connection errors, always retry
                    if isinstance(e, (Timeout, ConnectionError)):
                        self.logger.warning(f"Network error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                        time.sleep(delay)
                        continue
                    
                    # For other API errors, retry with backoff
                    self.logger.warning(f"API error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                    time.sleep(delay)
                    continue
                else:
                    # Max retries exceeded
                    raise NotionError(f"Failed to upload file {file_path} after {max_retries + 1} attempts: {e}") from e
                    
            except Exception as e:
                # Non-retryable errors
                raise NotionError(f"Error uploading file {file_path}: {e}") from e
    
    def _get_content_type(self, file_path: Path) -> str:
        """
        Get content type for file.
        
        Args:
            file_path: Path to file
            
        Returns:
            MIME content type
        """
        import mimetypes
        content_type, _ = mimetypes.guess_type(str(file_path))
        return content_type or "application/octet-stream"
    
    def create_database(self, parent_page_id: str, title: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a database using the official API with retry logic.
        
        Args:
            parent_page_id: Parent page ID
            title: Database title
            properties: Database properties schema
            
        Returns:
            Created database data
        """
        import time
        import random
        from requests.exceptions import Timeout, ConnectionError
        from notion_client.errors import APIResponseError
        
        max_retries = 5
        base_delay = 2.0
        
        for attempt in range(max_retries + 1):
            try:
                response = self.client.databases.create(
                    parent={"type": "page_id", "page_id": parent_page_id},
                    title=[{"type": "text", "text": {"content": title}}],
                    properties=properties
                )
                return response
                
            except (APIResponseError, Timeout, ConnectionError) as e:
                # Check if this is a retryable error
                if attempt < max_retries:
                    # Calculate exponential backoff with jitter
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    
                    # Check for specific error codes that should be retried
                    if hasattr(e, 'status_code'):
                        if e.status_code in [503, 504, 429, 409]:  # Service unavailable, Gateway timeout, Rate limited, Conflict
                            self.logger.warning(f"Retryable error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                            time.sleep(delay)
                            continue
                        elif e.status_code in [400, 401, 403, 404]:  # Client errors - don't retry
                            raise NotionError(f"Failed to create database: {e}") from e
                    
                    # For timeout and connection errors, always retry
                    if isinstance(e, (Timeout, ConnectionError)):
                        self.logger.warning(f"Network error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                        time.sleep(delay)
                        continue
                    
                    # For other API errors, retry with backoff
                    self.logger.warning(f"API error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                    time.sleep(delay)
                    continue
                else:
                    # Max retries exceeded
                    raise NotionError(f"Failed to create database after {max_retries + 1} attempts: {e}") from e
                    
            except Exception as e:
                # Non-retryable errors
                raise NotionError(f"Error creating database: {e}") from e
    
    def create_page(self, parent: Dict[str, Any], properties: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Create a page using the official API with retry logic.
        
        Args:
            parent: Parent object (database or page)
            properties: Page properties
            **kwargs: Additional parameters
            
        Returns:
            Created page data
        """
        import time
        import random
        from requests.exceptions import Timeout, ConnectionError
        from notion_client.errors import APIResponseError
        
        max_retries = 5
        base_delay = 2.0
        
        for attempt in range(max_retries + 1):
            try:
                response = self.client.pages.create(
                    parent=parent,
                    properties=properties,
                    **kwargs
                )
                return response
                
            except (APIResponseError, Timeout, ConnectionError) as e:
                # Check if this is a retryable error
                if attempt < max_retries:
                    # Calculate exponential backoff with jitter
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    
                    # Check for specific error codes that should be retried
                    if hasattr(e, 'status_code'):
                        if e.status_code in [503, 504, 429, 409]:  # Service unavailable, Gateway timeout, Rate limited, Conflict
                            self.logger.warning(f"Retryable error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                            time.sleep(delay)
                            continue
                        elif e.status_code in [400, 401, 403, 404]:  # Client errors - don't retry
                            raise NotionError(f"Failed to create page: {e}") from e
                    
                    # For timeout and connection errors, always retry
                    if isinstance(e, (Timeout, ConnectionError)):
                        self.logger.warning(f"Network error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                        time.sleep(delay)
                        continue
                    
                    # For other API errors, retry with backoff
                    self.logger.warning(f"API error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                    time.sleep(delay)
                    continue
                else:
                    # Max retries exceeded
                    raise NotionError(f"Failed to create page after {max_retries + 1} attempts: {e}") from e
                    
            except Exception as e:
                # Non-retryable errors
                raise NotionError(f"Error creating page: {e}") from e
    
    def update_page(self, page_id: str, properties: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Update a page using the official API.
        
        Args:
            page_id: Page ID
            properties: Page properties to update
            **kwargs: Additional parameters
            
        Returns:
            Updated page data
        """
        try:
            response = self.client.pages.update(
                page_id=page_id,
                properties=properties,
                **kwargs
            )
            return response
        except APIResponseError as e:
            raise NotionError(f"Failed to update page {page_id}: {e}") from e
    
    def query_database(self, database_id: str, **kwargs) -> Dict[str, Any]:
        """
        Query a database using the official API.
        
        Args:
            database_id: Database ID
            **kwargs: Query parameters
            
        Returns:
            Query results
        """
        try:
            response = self.client.databases.query(
                database_id=database_id,
                **kwargs
            )
            return response
        except APIResponseError as e:
            raise NotionError(f"Failed to query database {database_id}: {e}") from e


def get_notion_client_official(
    integration_token: str, 
    workspace: Optional[str] = None, 
    **options
) -> NotionClientOfficial:
    """
    Factory function to create official Notion client - maintains compatibility.
    
    Args:
        integration_token: Notion integration token
        workspace: Workspace name (for compatibility)
        **options: Additional options
        
    Returns:
        NotionClientOfficial instance
    """
    try:
        client = NotionClientOfficial(
            integration_token=integration_token,
            workspace=workspace,
            **options
        )
        return client
    except Exception as e:
        raise NotionError(f"Failed to initialize Notion client: {e}") from e
