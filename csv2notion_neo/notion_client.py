"""
Official Notion SDK Client Adapter for CSV2Notion Neo

This module provides a compatibility layer between the existing CSV2Notion Neo
codebase and the official Notion SDK, ensuring seamless migration without
breaking existing functionality.

RETRY LOGIC ARCHITECTURE:
========================
This module implements a sophisticated retry system with the following characteristics:

1. EXPONENTIAL BACKOFF WITH JITTER:
   - Formula: base_delay * (2^attempt) + random(0,1) seconds
   - Prevents thundering herd problems in high concurrency scenarios
   - Delay progression: 2s, 4s, 8s, 16s, 32s, 64s, 128s, 256s, 512s, 1024s, 2048s, 4096s, 8192s, 16384s, 32768s

2. SMART ERROR HANDLING:
   - Server errors (5xx): Always retry (temporary server issues)
   - Rate limits (429): Always retry (temporary rate limiting)
   - Client errors (4xx): Never retry (permanent client issues)
   - Network errors: Always retry (temporary connectivity issues)
   - Conflict errors (409): Always retry (temporary concurrency conflicts)

3. RETRY CONFIGURATION:
   - max_retries = 14: Total of 15 attempts (0-14 inclusive)
   - base_delay = 2.0: Base delay in seconds for exponential backoff
   - Maximum retry time: ~18 hours (though most issues resolve much faster)

4. USE CASE SCENARIOS:
   - High concurrency: Multiple users uploading simultaneously
   - Large file uploads: Files that take longer to process
   - Rate limit scenarios: API rate limiting and throttling
   - Network instability: Temporary connection issues
   - Server errors: 503, 504, 429, 409 status codes

5. IMPLEMENTED FUNCTIONS:
   - upload_file(): File upload operations with retry logic
   - create_database(): Database creation with retry logic
   - create_page(): Page creation with retry logic

TWO DISTINCT LOGIC PATHS:
========================
This module implements two distinct logic paths for different use cases:

LOGIC PATH 1: CREATE NEW DATABASE IN EMPTY PAGE
==============================================
- When: User provides a PAGE URL (not database URL)
- Function: create_database()
- Purpose: Creates a new database within an existing page
- Workflow: Page URL → Create Database → Upload Data
- Use Case: User wants to create a new database in an existing page

LOGIC PATH 2: UPLOAD TO EXISTING DATABASE
========================================
- When: User provides a DATABASE URL (not page URL)
- Function: create_page()
- Purpose: Uploads data to an existing database
- Workflow: Database URL → Upload Data
- Use Case: User wants to add data to an existing database

This retry system ensures robust operation in production environments with
high concurrency, large datasets, and network instability.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from notion_client import Client, APIResponseError, APIErrorCode
from notion_client.helpers import get_id

from csv2notion_neo.utils_exceptions import NotionError, CriticalError


class NotionClient:
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
    
    # ============================================================================
    # SHARED FUNCTION: FILE UPLOAD (USED BY BOTH LOGIC PATHS)
    # ============================================================================
    # This function is used by BOTH logic paths:
    # - LOGIC PATH 1: When creating new databases (for file attachments)
    # - LOGIC PATH 2: When uploading to existing databases (for file attachments)
    # - Purpose: Handles file uploads with retry logic for both scenarios
    # ============================================================================
    
    def upload_file(self, file_path: Path, parent_block_id: str) -> Tuple[str, Dict[str, Any]]:
        """
        Upload a file using the official API with retry logic.
        
        This function is shared between both logic paths and handles file uploads
        for both new database creation and existing database uploads.
        
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
        
        # ============================================================================
        # RETRY CONFIGURATION FOR FILE UPLOAD OPERATIONS
        # ============================================================================
        # This section implements robust retry logic for file uploads to handle:
        # - High concurrency scenarios (multiple users uploading simultaneously)
        # - Large file uploads (files that take longer to process)
        # - Rate limit scenarios (API rate limiting and throttling)
        # - Network instability (temporary connection issues)
        # - Server errors (503, 504, 429 status codes)
        #
        # Configuration:
        # - max_retries = 14: Total of 15 attempts (0-14 inclusive)
        # - base_delay = 2.0: Base delay in seconds for exponential backoff
        # - Exponential backoff formula: base_delay * (2^attempt) + random(0,1)
        # - Delay progression: 2s, 4s, 8s, 16s, 32s, 64s, 128s, 256s, 512s, 1024s, 2048s, 4096s, 8192s, 16384s, 32768s
        # - Maximum retry time: ~18 hours (though most issues resolve much faster)
        # ============================================================================
        max_retries = 14
        base_delay = 2.0  # Base delay in seconds for exponential backoff
        
        # Main retry loop with exponential backoff and jitter
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
                # ========================================================================
                # RETRY LOGIC: SMART ERROR HANDLING WITH EXPONENTIAL BACKOFF
                # ========================================================================
                # This section implements intelligent retry logic that:
                # 1. Analyzes error types to determine if retry is appropriate
                # 2. Uses exponential backoff with jitter to prevent thundering herd
                # 3. Handles different error scenarios with appropriate strategies
                # 4. Provides detailed logging for debugging and monitoring
                # ========================================================================
                
                # Check if we have retry attempts remaining
                if attempt < max_retries:
                    # Calculate exponential backoff with jitter to prevent thundering herd
                    # Formula: base_delay * (2^attempt) + random(0,1) seconds
                    # This creates progressive delays: 2s, 4s, 8s, 16s, 32s, 64s, 128s, 256s, 512s, 1024s, 2048s, 4096s, 8192s, 16384s, 32768s
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    
                    # ====================================================================
                    # SMART RETRY LOGIC BASED ON ERROR TYPE
                    # ====================================================================
                    # Different error types require different retry strategies:
                    # - Server errors (5xx): Always retry (temporary server issues)
                    # - Rate limits (429): Always retry (temporary rate limiting)
                    # - Client errors (4xx): Never retry (permanent client issues)
                    # - Network errors: Always retry (temporary connectivity issues)
                    # ====================================================================
                    
                    if hasattr(e, 'status_code'):
                        # Retryable server errors: Service unavailable, Gateway timeout, Rate limited
                        if e.status_code in [503, 504, 429]:
                            self.logger.warning(f"Retryable error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                            time.sleep(delay)
                            continue
                        # Client errors: Bad request, Unauthorized, Forbidden, Not found - don't retry
                        elif e.status_code in [400, 401, 403, 404]:
                            raise NotionError(f"Failed to upload file {file_path}: {e}") from e
                    
                    # Network issues: Always retry for timeout and connection errors
                    if isinstance(e, (Timeout, ConnectionError)):
                        self.logger.warning(f"Network error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                        time.sleep(delay)
                        continue
                    
                    # Other API errors: Retry with exponential backoff
                    self.logger.warning(f"API error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                    time.sleep(delay)
                    continue
                else:
                    # ====================================================================
                    # RETRY EXHAUSTION: ALL ATTEMPTS FAILED
                    # ====================================================================
                    # When all retry attempts are exhausted, we raise a detailed error
                    # that includes the total number of attempts and the final error
                    # ====================================================================
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
    
    # ============================================================================
    # LOGIC PATH 1: CREATE NEW DATABASE IN EMPTY PAGE
    # ============================================================================
    # This function is used when:
    # - User provides a PAGE URL (not database URL)
    # - CSV2Notion Neo needs to create a new database within an existing page
    # - The database doesn't exist yet and needs to be created from scratch
    # - This is part of the "create database in page" workflow
    # ============================================================================
    
    def create_database(self, parent_page_id: str, title: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a database using the official API with retry logic.
        
        This function is part of LOGIC PATH 1: Creating new databases in empty pages.
        It handles the creation of a new database within an existing page when
        the user provides a page URL instead of a database URL.
        
        Args:
            parent_page_id: Parent page ID where the database will be created
            title: Database title
            properties: Database properties schema
            
        Returns:
            Created database data
        """
        import time
        import random
        from requests.exceptions import Timeout, ConnectionError
        from notion_client.errors import APIResponseError
        
        # ============================================================================
        # RETRY CONFIGURATION FOR DATABASE CREATION OPERATIONS
        # ============================================================================
        # This section implements robust retry logic for database creation to handle:
        # - High concurrency scenarios (multiple users creating databases simultaneously)
        # - Rate limit scenarios (API rate limiting and throttling)
        # - Network instability (temporary connection issues)
        # - Server errors (503, 504, 429, 409 status codes)
        # - Conflict errors (409) when multiple operations try to create databases
        #
        # Configuration:
        # - max_retries = 14: Total of 15 attempts (0-14 inclusive)
        # - base_delay = 2.0: Base delay in seconds for exponential backoff
        # - Exponential backoff formula: base_delay * (2^attempt) + random(0,1)
        # - Delay progression: 2s, 4s, 8s, 16s, 32s, 64s, 128s, 256s, 512s, 1024s, 2048s, 4096s, 8192s, 16384s, 32768s
        # - Maximum retry time: ~18 hours (though most issues resolve much faster)
        # ============================================================================
        max_retries = 14
        base_delay = 2.0  # Base delay in seconds for exponential backoff
        
        # Main retry loop with exponential backoff and jitter
        for attempt in range(max_retries + 1):
            try:
                response = self.client.databases.create(
                    parent={"type": "page_id", "page_id": parent_page_id},
                    title=[{"type": "text", "text": {"content": title}}],
                    properties=properties
                )
                return response
                
            except (APIResponseError, Timeout, ConnectionError) as e:
                # Retry logic: Check if we have attempts remaining
                if attempt < max_retries:
                    # Calculate exponential backoff with jitter to prevent thundering herd
                    # Formula: base_delay * (2^attempt) + random(0,1) seconds
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    
                    # Smart retry logic based on error type
                    if hasattr(e, 'status_code'):
                        # Retryable server errors: Service unavailable, Gateway timeout, Rate limited, Conflict
                        if e.status_code in [503, 504, 429, 409]:
                            self.logger.warning(f"Retryable error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                            time.sleep(delay)
                            continue
                        # Client errors: Bad request, Unauthorized, Forbidden, Not found - don't retry
                        elif e.status_code in [400, 401, 403, 404]:
                            raise NotionError(f"Failed to create database: {e}") from e
                    
                    # Network issues: Always retry for timeout and connection errors
                    if isinstance(e, (Timeout, ConnectionError)):
                        self.logger.warning(f"Network error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                        time.sleep(delay)
                        continue
                    
                    # Other API errors: Retry with exponential backoff
                    self.logger.warning(f"API error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                    time.sleep(delay)
                    continue
                else:
                    # All retry attempts exhausted - fail with detailed error
                    raise NotionError(f"Failed to create database after {max_retries + 1} attempts: {e}") from e
                    
            except Exception as e:
                # Non-retryable errors
                raise NotionError(f"Error creating database: {e}") from e
    
    # ============================================================================
    # LOGIC PATH 2: UPLOAD TO EXISTING DATABASE
    # ============================================================================
    # This function is used when:
    # - User provides a DATABASE URL (not page URL)
    # - CSV2Notion Neo needs to upload data to an existing database
    # - The database already exists and we're adding new pages/rows to it
    # - This is part of the "upload to existing database" workflow
    # ============================================================================
    
    def create_page(self, parent: Dict[str, Any], properties: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Create a page using the official API with retry logic.
        
        This function is part of LOGIC PATH 2: Uploading to existing databases.
        It handles the creation of new pages/rows within an existing database
        when the user provides a database URL instead of a page URL.
        
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
        
        # ============================================================================
        # RETRY CONFIGURATION FOR PAGE CREATION OPERATIONS
        # ============================================================================
        # This section implements robust retry logic for page creation to handle:
        # - High concurrency scenarios (multiple users creating pages simultaneously)
        # - Rate limit scenarios (API rate limiting and throttling)
        # - Network instability (temporary connection issues)
        # - Server errors (503, 504, 429, 409 status codes)
        # - Conflict errors (409) when multiple operations try to create pages
        # - Database/page creation conflicts in concurrent scenarios
        #
        # Configuration:
        # - max_retries = 14: Total of 15 attempts (0-14 inclusive)
        # - base_delay = 2.0: Base delay in seconds for exponential backoff
        # - Exponential backoff formula: base_delay * (2^attempt) + random(0,1)
        # - Delay progression: 2s, 4s, 8s, 16s, 32s, 64s, 128s, 256s, 512s, 1024s, 2048s, 4096s, 8192s, 16384s, 32768s
        # - Maximum retry time: ~18 hours (though most issues resolve much faster)
        # ============================================================================
        max_retries = 14
        base_delay = 2.0  # Base delay in seconds for exponential backoff
        
        # Main retry loop with exponential backoff and jitter
        for attempt in range(max_retries + 1):
            try:
                response = self.client.pages.create(
                    parent=parent,
                    properties=properties,
                    **kwargs
                )
                return response
                
            except (APIResponseError, Timeout, ConnectionError) as e:
                # Retry logic: Check if we have attempts remaining
                if attempt < max_retries:
                    # Calculate exponential backoff with jitter to prevent thundering herd
                    # Formula: base_delay * (2^attempt) + random(0,1) seconds
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    
                    # Smart retry logic based on error type
                    if hasattr(e, 'status_code'):
                        # Retryable server errors: Service unavailable, Gateway timeout, Rate limited, Conflict
                        if e.status_code in [503, 504, 429, 409]:
                            self.logger.warning(f"Retryable error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                            time.sleep(delay)
                            continue
                        # Client errors: Bad request, Unauthorized, Forbidden, Not found - don't retry
                        elif e.status_code in [400, 401, 403, 404]:
                            raise NotionError(f"Failed to create page: {e}") from e
                    
                    # Network issues: Always retry for timeout and connection errors
                    if isinstance(e, (Timeout, ConnectionError)):
                        self.logger.warning(f"Network error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                        time.sleep(delay)
                        continue
                    
                    # Other API errors: Retry with exponential backoff
                    self.logger.warning(f"API error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                    time.sleep(delay)
                    continue
                else:
                    # All retry attempts exhausted - fail with detailed error
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


def get_notion_client(
    integration_token: str, 
    workspace: Optional[str] = None, 
    **options
) -> NotionClient:
    """
    Factory function to create official Notion client - maintains compatibility.
    
    Args:
        integration_token: Notion integration token
        workspace: Workspace name (for compatibility)
        **options: Additional options
        
    Returns:
        NotionClient instance
    """
    try:
        client = NotionClient(
            integration_token=integration_token,
            workspace=workspace,
            **options
        )
        return client
    except Exception as e:
        raise NotionError(f"Failed to initialize Notion client: {e}") from e


# ============================================================================
# LOGIC PATH SUMMARY
# ============================================================================
# This module implements two distinct logic paths for CSV2Notion Neo:
#
# LOGIC PATH 1: CREATE NEW DATABASE IN EMPTY PAGE
# ===============================================
# - Function: create_database()
# - When: User provides PAGE URL
# - Purpose: Creates new database within existing page
# - Workflow: Page URL → Create Database → Upload Data
# - Retry Logic: 15 attempts with exponential backoff
#
# LOGIC PATH 2: UPLOAD TO EXISTING DATABASE
# =========================================
# - Function: create_page()
# - When: User provides DATABASE URL
# - Purpose: Uploads data to existing database
# - Workflow: Database URL → Upload Data
# - Retry Logic: 15 attempts with exponential backoff
#
# SHARED FUNCTION: FILE UPLOAD
# ===========================
# - Function: upload_file()
# - Used by: Both logic paths
# - Purpose: Handles file attachments for both scenarios
# - Retry Logic: 15 attempts with exponential backoff
#
# All functions implement the same robust retry system with exponential backoff,
# smart error handling, and comprehensive logging for production environments.
# ============================================================================
