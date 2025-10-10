"""
Official Notion SDK Database Operations for CSV2Notion Neo

This module provides database operations using the official Notion SDK,
maintaining compatibility with the existing CSV2Notion Neo codebase.
"""

import logging
import random
import re
import threading
from typing import Any, Dict, List, Optional, Tuple

from csv2notion_neo.notion_client import NotionClient
from csv2notion_neo.local_data import LocalData
from csv2notion_neo.utils_exceptions import NotionError
from csv2notion_neo.utils_rand_id import rand_id_list
from csv2notion_neo.utils_db import make_status_column

logger = logging.getLogger(__name__)

# Notion API supported colors for select options
NOTION_COLORS = [
    "blue", "brown", "default", "gray", "green",
    "orange", "pink", "purple", "red", "yellow"
]


def _get_random_select_color() -> str:
    """Get a random color for select options."""
    return random.choice(NOTION_COLORS)


class NotionDB:
    """
    Official Notion SDK database operations adapter.
    Maintains compatibility with existing NotionDB interface.
    """
    
    def __init__(self, client: NotionClient, collection_id: str):
        """
        Initialize database operations.
        
        Args:
            client: Official Notion client
            collection_id: Database/collection ID
        """
        self.client = client
        self.collection_id = collection_id
        self.logger = logging.getLogger(__name__)
        self._option_lock = threading.Lock()  # Lock for preventing race conditions when adding select options
        
        # Cache for performance
        self._cache_columns: Optional[Dict[str, Dict[str, str]]] = None
        self._cache_relations: Optional[Dict[str, "NotionDB"]] = None
        self._cache_rows: Optional[Dict[str, Dict[str, Any]]] = None
        self._cache_users: Optional[Dict[str, Dict[str, Any]]] = None
        
        # Get database info
        self._database_info = self._get_database_info()
    
    def _get_database_info(self) -> Dict[str, Any]:
        """Get database information."""
        try:
            return self.client.get_collection(self.collection_id)
        except Exception as e:
            self.logger.error(f"Failed to get database info: {e}")
            raise NotionError(f"Cannot access database {self.collection_id}") from e
    
    @property
    def name(self) -> str:
        """Get database name."""
        title = self._database_info.get("title", [])
        if title and len(title) > 0:
            return title[0].get("text", {}).get("content", "Untitled Database")
        return "Untitled Database"
    
    @property
    def columns(self) -> Dict[str, Dict[str, str]]:
        """Get database columns/properties."""
        if self._cache_columns is None:
            properties = self._database_info.get("properties", {})
            self._cache_columns = {}
            
            for prop_id, prop_data in properties.items():
                prop_name = prop_data.get("name", "")
                prop_type = prop_data.get("type", "")
                
                self._cache_columns[prop_name] = {
                    "name": prop_name,
                    "type": prop_type,
                    "id": prop_id
                }
                
                # Add additional type-specific info
                if prop_type == "select":
                    options = prop_data.get("select", {}).get("options", [])
                    self._cache_columns[prop_name]["options"] = [
                        {"name": opt.get("name", ""), "color": opt.get("color", "default")}
                        for opt in options
                    ]
                elif prop_type == "multi_select":
                    options = prop_data.get("multi_select", {}).get("options", [])
                    self._cache_columns[prop_name]["options"] = [
                        {"name": opt.get("name", ""), "color": opt.get("color", "default")}
                        for opt in options
                    ]
                elif prop_type == "status":
                    options = prop_data.get("status", {}).get("options", [])
                    self._cache_columns[prop_name]["options"] = [
                        {"name": opt.get("name", ""), "color": opt.get("color", "default")}
                        for opt in options
                    ]
                elif prop_type == "relation":
                    relation_data = prop_data.get("relation", {})
                    self._cache_columns[prop_name]["collection_id"] = relation_data.get("database_id", "")
        
        return self._cache_columns
    
    @property
    def key_column(self) -> str:
        """Get the title column (key column)."""
        for col_name, col_data in self.columns.items():
            if col_data["type"] == "title":
                return col_name
        
        # Fallback to first column if no title found
        if self.columns:
            return list(self.columns.keys())[0]
        
        raise NotionError("No columns found in database")
    
    @property
    def rows(self) -> Dict[str, Dict[str, Any]]:
        """Get database rows."""
        if self._cache_rows is None:
            self._cache_rows = {}
            
            try:
                # Query all pages in the database
                response = self.client.query_database(self.collection_id)
                
                for page in response.get("results", []):
                    # Get the title property value
                    title_prop = None
                    for prop_name, prop_data in self.columns.items():
                        if prop_data["type"] == "title":
                            title_prop = prop_name
                            break
                    
                    if title_prop:
                        title_data = page.get("properties", {}).get(title_prop, {})
                        title_text = ""
                        
                        if title_data.get("title"):
                            title_text = "".join([
                                text.get("text", {}).get("content", "")
                                for text in title_data["title"]
                            ])
                        
                        if title_text:
                            self._cache_rows[title_text] = page
                
            except Exception as e:
                self.logger.error(f"Failed to get database rows: {e}")
                raise NotionError(f"Cannot query database {self.collection_id}") from e
        
        return self._cache_rows
    
    @property
    def relations(self) -> Dict[str, "NotionDB"]:
        """Get related databases."""
        if self._cache_relations is None:
            self._cache_relations = {}
            
            for col_name, col_data in self.columns.items():
                if col_data["type"] == "relation":
                    collection_id = col_data.get("collection_id")
                    if collection_id:
                        self._cache_relations[col_name] = NotionDB(
                            self.client, collection_id
                        )
        
        return self._cache_relations
    
    @property
    def users(self) -> Dict[str, Dict[str, Any]]:
        """Get workspace users."""
        if self._cache_users is None:
            self._cache_users = {}
            
            try:
                users = self.client.current_space.get("users", [])
                for user in users:
                    email = user.get("person", {}).get("email", "")
                    if email:
                        self._cache_users[email] = user
            except Exception as e:
                self.logger.warning(f"Failed to get users: {e}")
        
        return self._cache_users
    
    def get_user_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get user by name."""
        for user in self.users.values():
            if user.get("name") == name:
                return user
        return None
    
    def find_user(self, email: str) -> Optional[Dict[str, Any]]:
        """Find user by email."""
        if email in self.users:
            return self.users[email]
        
        # Try to find user via API
        try:
            response = self.client.post("findUser", {"email": email})
            user_id = response.get("value", {}).get("value", {}).get("id")
            
            if user_id:
                # Find user in workspace users
                for user in self.client.current_space.get("users", []):
                    if user.get("id") == user_id:
                        self.users[email] = user
                        return user
        except Exception as e:
            self.logger.warning(f"Failed to find user {email}: {e}")
        
        return None
    
    def has_duplicates(self) -> bool:
        """Check if database has duplicate entries."""
        # This would need to be implemented based on your specific logic
        # For now, return False as a placeholder
        return False
    
    def is_accessible(self) -> bool:
        """Check if database is accessible."""
        try:
            self.client.get_collection(self.collection_id)
            return True
        except Exception:
            return False
    
    def add_column(self, column_name: str, column_type: str) -> None:
        """Add a column to the database."""
        try:
            # Update database properties
            properties = self._database_info.get("properties", {})
            
            # Generate new property ID
            prop_id = rand_id_list(1, 4)[0]
            
            # Create property schema based on type
            prop_schema = {"name": column_name, "type": column_type}
            
            if column_type == "status":
                prop_schema.update(make_status_column())
            elif column_type == "select":
                prop_schema["select"] = {"options": []}
            elif column_type == "multi_select":
                prop_schema["multi_select"] = {"options": []}
            
            properties[prop_id] = prop_schema
            
            # Update database
            self.client.client.databases.update(
                database_id=self.collection_id,
                properties=properties
            )
            
            # Clear cache
            self._cache_columns = None
            self._database_info = self._get_database_info()
            
        except Exception as e:
            raise NotionError(f"Failed to add column {column_name}: {e}") from e
    
    def add_select_option(self, prop_name: str, option_name: str, color: Optional[str] = None) -> None:
        """Add a new option to a select, multi_select, or status property."""
        # Use lock to prevent race conditions when multiple threads try to add the same option
        with self._option_lock:
            try:
                if prop_name not in self.columns:
                    raise NotionError(f"Property '{prop_name}' not found in database")
                
                prop_info = self.columns[prop_name]
                prop_type = prop_info["type"]
                
                if prop_type not in ["select", "multi_select", "status"]:
                    raise NotionError(f"Property '{prop_name}' is not a select, multi_select, or status type")
                
                # Get current options
                current_options = prop_info.get("options", [])
                
                # Check if option already exists
                existing_names = [opt["name"] for opt in current_options]
                if option_name in existing_names:
                    # Option already exists, no need to add it
                    return
                
                # Determine color
                if color is None:
                    # Check if we should randomize colors
                    if hasattr(self.client, 'options') and self.client.options.get("is_randomize_select_colors"):
                        color = _get_random_select_color()
                    else:
                        color = "default"
                
                # Create new option
                new_option = {
                    "name": option_name,
                    "color": color
                }
                
                # Add to existing options
                updated_options = current_options + [new_option]
                
                # Update the database property
                self.client.client.databases.update(
                    database_id=self.collection_id,
                    properties={
                        prop_name: {
                            prop_type: {
                                "options": updated_options
                            }
                        }
                    }
                )
                
                # Clear cache to refresh schema
                self._cache_columns = None
                self._database_info = self._get_database_info()
                
                # Commented out for cleaner output - uncomment for debugging
                # logger.debug(f"Added option '{option_name}' with color '{color}' to property '{prop_name}'")
                
            except Exception as e:
                raise NotionError(f"Failed to add select option '{option_name}' to property '{prop_name}': {e}") from e
    
    def delete_all_entries(self) -> int:
        """
        Delete (archive) all entries in the database.
        
        Returns:
            Number of entries deleted
        """
        from tqdm import tqdm
        import time
        
        deleted_count = 0
        all_pages = []
        
        try:
            # First, collect all pages with pagination
            has_more = True
            next_cursor = None
            
            while has_more:
                # Query database for all pages
                response = self.client.query_database(
                    self.collection_id,
                    start_cursor=next_cursor,
                    page_size=100  # Maximum page size
                )
                
                all_pages.extend(response.get("results", []))
                
                # Check if there are more pages
                has_more = response.get("has_more", False)
                next_cursor = response.get("next_cursor")
            
            # Check if database is empty
            if not all_pages:
                self.logger.info("Database is empty - no entries to delete")
                return 0
            
            # Now archive all pages with progress bar
            with tqdm(total=len(all_pages), desc="Deleting database entries", unit="entries", leave=False) as pbar:
                for page in all_pages:
                    page_id = page["id"]
                    try:
                        # Archive the page (soft delete)
                        self.client.client.pages.update(
                            page_id=page_id,
                            archived=True
                        )
                        deleted_count += 1
                        
                        # Rate limiting: wait 0.35 seconds between requests
                        time.sleep(0.35)
                        
                    except Exception as e:
                        logger.warning(f"Failed to archive page {page_id}: {e}")
                        continue
                    
                    pbar.update(1)
            
            # Clear cache since we've modified the database
            self._cache_rows = None
            
            return deleted_count
            
        except Exception as e:
            raise NotionError(f"Failed to delete all database entries: {e}") from e
    
    def add_row(
        self,
        properties: Optional[Dict[str, Any]] = None,
        columns: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Add a row to the database."""
        import time
        from notion_client.errors import APIResponseError
        
        max_retries = 3
        retry_delay = 1.0  # Start with 1 second delay
        
        for attempt in range(max_retries):
            try:
                # Convert columns to properties format
                notion_properties = {}
                
                if columns:
                    for col_name, value in columns.items():
                        if col_name in self.columns:
                            col_type = self.columns[col_name]["type"]
                            converted_property = self._convert_value_to_notion_property(
                                value, col_type, col_name
                            )
                            # Only include properties that are not None or empty
                            if converted_property and converted_property != {}:
                                notion_properties[col_name] = converted_property
                
                if properties:
                    # Convert any PosixPath objects in properties to strings
                    converted_properties = self._convert_paths_to_strings(properties)
                    # Only include properties that exist in the database schema
                    for prop_name, prop_value in converted_properties.items():
                        if prop_name in self.columns:
                            col_type = self.columns[prop_name]["type"]
                            converted_property = self._convert_value_to_notion_property(
                                prop_value, col_type, prop_name
                            )
                            # Only include properties that are not None or empty
                            if converted_property and converted_property != {}:
                                notion_properties[prop_name] = converted_property
                
                    # Debug: Log the properties we're about to send
                    # logger.debug(f"Creating page with properties: {notion_properties}")
                
                # Create page
                response = self.client.create_page(
                    parent={"database_id": self.collection_id},
                    properties=notion_properties
                )
                
                # Update cache immediately to prevent race conditions
                if columns and self.key_column in columns:
                    key_value = columns[self.key_column]
                    if self._cache_rows is not None:
                        self._cache_rows[key_value] = response
                
                return response
                
            except APIResponseError as e:
                if e.code == "conflict_error" and attempt < max_retries - 1:
                    # Database might not be ready yet, wait and retry
                    self.logger.warning(f"Database conflict on attempt {attempt + 1}, retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                else:
                    raise NotionError(f"Failed to add row: {e}") from e
            except Exception as e:
                raise NotionError(f"Failed to add row: {e}") from e
    
    def add_row_key(self, key: str) -> Dict[str, Any]:
        """Add a row with just a key value."""
        return self.add_row(columns={self.key_column: key})
    
    def invalidate_cache(self) -> None:
        """Invalidate all cached data to force fresh data retrieval."""
        self._cache_columns = None
        self._cache_relations = None
        self._cache_rows = None
        self._cache_users = None
        self._database_info = self._get_database_info()
    
    def update_row(self, page_id: str, properties: Optional[Dict[str, Any]] = None, columns: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Update an existing row/page."""
        try:
            # Convert columns to properties format
            notion_properties = {}
            
            if columns:
                for col_name, value in columns.items():
                    if col_name in self.columns:
                        col_type = self.columns[col_name]["type"]
                        converted_property = self._convert_value_to_notion_property(
                            value, col_type, col_name
                        )
                        # Only include properties that are not None or empty
                        if converted_property and converted_property != {}:
                            notion_properties[col_name] = converted_property
            
            if properties:
                # Convert any PosixPath objects in properties to strings
                converted_properties = self._convert_paths_to_strings(properties)
                # Only include properties that exist in the database schema
                for prop_name, prop_value in converted_properties.items():
                    if prop_name in self.columns:
                        col_type = self.columns[prop_name]["type"]
                        converted_property = self._convert_value_to_notion_property(
                            prop_value, col_type, prop_name
                        )
                        # Only include properties that are not None or empty
                        if converted_property and converted_property != {}:
                            notion_properties[prop_name] = converted_property
            
            # Update page
            response = self.client.client.pages.update(
                page_id=page_id,
                properties=notion_properties
            )
            
            # Update cache to reflect the changes
            if columns and self.key_column in columns:
                key_value = columns[self.key_column]
                if self._cache_rows is not None:
                    self._cache_rows[key_value] = response
            
            return response
            
        except Exception as e:
            raise NotionError(f"Failed to update row: {e}") from e
    
    def _convert_paths_to_strings(self, data: Any) -> Any:
        """Recursively convert PosixPath objects to strings in nested data structures."""
        if hasattr(data, '__fspath__'):  # Path-like objects
            return str(data)
        elif isinstance(data, dict):
            return {key: self._convert_paths_to_strings(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._convert_paths_to_strings(item) for item in data]
        else:
            return data

    def _convert_value_to_notion_property(self, value: Any, prop_type: str, prop_name: str = None) -> Dict[str, Any]:
        """Convert a value to Notion property format."""
        # Convert PosixPath objects to strings
        if hasattr(value, '__fspath__'):  # Path-like objects
            value = str(value)
        
        if prop_type == "title":
            if value is None or value == "":
                return {"title": []}
            return {"title": [{"text": {"content": str(value)}}]}
        elif prop_type == "rich_text":
            if value is None or value == "":
                return {"rich_text": []}
            return {"rich_text": [{"text": {"content": str(value)}}]}
        elif prop_type == "number":
            if value is None or value == "":
                return None
            try:
                return {"number": float(value)}
            except (ValueError, TypeError):
                return None
        elif prop_type == "select":
            if value is None or value == "":
                return None
            
            # Check if the select option exists in the database schema
            if prop_name and prop_name in self.columns:
                available_options = self.columns[prop_name].get("options", [])
                option_names = [opt["name"] for opt in available_options]
                
                if str(value) not in option_names:
                    # Automatically add the new select option
                    # Commented out for cleaner output - uncomment for debugging
                    # logger.info(f"Adding new select option '{value}' to property '{prop_name}'")
                    try:
                        self.add_select_option(prop_name, str(value))
                        # Refresh the columns cache to get the updated schema
                        self._cache_columns = None
                    except Exception as e:
                        # Commented out for cleaner output - uncomment for debugging
                        # logger.warning(f"Failed to add select option '{value}' to property '{prop_name}': {e}. Skipping property.")
                        return None
            
            return {"select": {"name": str(value)}}
        elif prop_type == "multi_select":
            if value is None or value == "":
                return {"multi_select": []}
            
            # Check if the multi_select options exist in the database schema
            if prop_name and prop_name in self.columns:
                available_options = self.columns[prop_name].get("options", [])
                option_names = [opt["name"] for opt in available_options]
                
                if isinstance(value, list):
                    valid_values = []
                    invalid_values = []
                    
                    for v in value:
                        if v and str(v) in option_names:
                            valid_values.append(str(v))
                        elif v:
                            invalid_values.append(str(v))
                    
                    # Automatically add new options for invalid values
                    if invalid_values:
                        # Commented out for cleaner output - uncomment for debugging
                        # logger.info(f"Adding new multi-select options {invalid_values} to property '{prop_name}'")
                        for invalid_value in invalid_values:
                            try:
                                self.add_select_option(prop_name, invalid_value)
                                valid_values.append(invalid_value)
                            except Exception as e:
                                # Commented out for cleaner output - uncomment for debugging
                                # logger.warning(f"Failed to add multi-select option '{invalid_value}' to property '{prop_name}': {e}")
                                pass
                        
                        # Refresh the columns cache to get the updated schema
                        if invalid_values:
                            self._cache_columns = None
                    
                    return {"multi_select": [{"name": v} for v in valid_values]}
                else:
                    if str(value) not in option_names:
                        # Automatically add the new multi-select option
                        logger.info(f"Adding new multi-select option '{value}' to property '{prop_name}'")
                        try:
                            self.add_select_option(prop_name, str(value))
                            # Refresh the columns cache to get the updated schema
                            self._cache_columns = None
                        except Exception as e:
                            logger.warning(f"Failed to add multi-select option '{value}' to property '{prop_name}': {e}. Skipping property.")
                            return {"multi_select": []}
                    return {"multi_select": [{"name": str(value)}]}
            
            # Fallback if we don't have schema info
            if isinstance(value, list):
                return {"multi_select": [{"name": str(v)} for v in value if v]}
            else:
                return {"multi_select": [{"name": str(value)}]}
        elif prop_type == "date":
            if value is None or value == "":
                return None
            # Value is already a dict from map_notion_date, wrap it as-is
            return {"date": value}
        elif prop_type == "checkbox":
            if value is None or value == "":
                return {"checkbox": False}
            return {"checkbox": bool(value)}
        elif prop_type == "url":
            if value is None or value == "":
                return None
            return {"url": str(value)}
        elif prop_type == "email":
            if value is None or value == "":
                return None
            return {"email": str(value)}
        elif prop_type == "phone_number":
            if value is None or value == "":
                return None
            return {"phone_number": str(value)}
        elif prop_type == "files":
            if value is None or value == "":
                return {"files": []}
            if isinstance(value, list):
                # Convert any Path objects in the list to strings
                converted_files = []
                for item in value:
                    if hasattr(item, '__fspath__'):
                        converted_files.append(str(item))
                    else:
                        converted_files.append(item)
                return {"files": converted_files}
            else:
                # Convert single Path object to string
                if hasattr(value, '__fspath__'):
                    return {"files": [str(value)]}
                else:
                    return {"files": [value]}
        elif prop_type == "people":
            if value is None or value == "":
                return {"people": []}
            if isinstance(value, list):
                return {"people": value}
            else:
                return {"people": [value]}
        elif prop_type == "relation":
            if value is None or value == "":
                return {"relation": []}
            if isinstance(value, list):
                return {"relation": value}
            else:
                return {"relation": [value]}
        elif prop_type == "status":
            if value is None or value == "":
                return None
            
            # Check if the status option exists in the database schema
            if prop_name and prop_name in self.columns:
                available_options = self.columns[prop_name].get("options", [])
                option_names = [opt["name"] for opt in available_options]
                
                if str(value) not in option_names:
                    # Automatically add the new status option
                    # Commented out for cleaner output - uncomment for debugging
                    # logger.info(f"Adding new status option '{value}' to property '{prop_name}'")
                    try:
                        self.add_select_option(prop_name, str(value))
                        # Refresh the columns cache to get the updated schema
                        self._cache_columns = None
                    except Exception as e:
                        # Commented out for cleaner output - uncomment for debugging
                        # logger.warning(f"Failed to add status option '{value}' to property '{prop_name}': {e}. Skipping property.")
                        return None
            
            return {"status": {"name": str(value)}}
        else:
            # Default to rich_text
            if value is None or value == "":
                return {"rich_text": []}
            return {"rich_text": [{"text": {"content": str(value)}}]}


def _extract_database_id_from_url(notion_url: str) -> str:
    """Extract database ID from Notion URL."""
    # Attempt to parse as a database ID directly
    if len(notion_url) == 32:  # Common length for Notion IDs
        return notion_url
    elif len(notion_url) == 36 and '-' in notion_url:  # Notion IDs with hyphens
        return notion_url

    # Attempt to parse as a URL
    from urllib.parse import urlparse
    parsed_url = urlparse(notion_url)
    path_parts = parsed_url.path.split('/')
    
    database_id = None
    # Look for ID in path (e.g., notion.so/database_id)
    for part in path_parts:
        if len(part) == 32:  # Notion IDs are 32 chars long without hyphens
            database_id = part
            break
        elif len(part) == 36 and '-' in part:  # Notion IDs are 36 chars long with hyphens
            database_id = part
            break

    if not database_id:
        # Fallback for URLs like https://www.notion.so/myorg/8511b9fc522249f79b90768b832599cc?v=...
        # The ID is usually the last part before '?' or '/'
        if len(path_parts[-1]) == 32 or (len(path_parts[-1]) == 36 and '-' in path_parts[-1]):
            database_id = path_parts[-1]
        elif len(path_parts[-2]) == 32 or (len(path_parts[-2]) == 36 and '-' in path_parts[-2]):
            database_id = path_parts[-2]

    if not database_id:
        raise NotionError("Could not extract database ID from the provided URL.")

    return database_id


def get_collection_id(client: NotionClient, notion_url: str) -> str:
    """
    Get collection ID from Notion URL - maintains compatibility.
    Handles both database URLs and page URLs (creates database in page).
    
    Args:
        client: Official Notion client
        notion_url: Notion URL
        
    Returns:
        Collection/database ID
    """
    try:
        # Extract ID from URL first
        notion_id = _extract_database_id_from_url(notion_url)
        
        # First, try to retrieve as a database
        try:
            database = client.client.databases.retrieve(database_id=notion_id)
            if database and database.get("object") == "database":
                return database["id"]
        except Exception:
            # If it fails, it might be a page URL
            pass
        
        # If not a database, try to retrieve as a page
        try:
            page = client.client.pages.retrieve(page_id=notion_id)
            if page and page.get("object") == "page":
                # This is a page URL - we need to create a database within this page
                # Return the page ID with a special marker to indicate it's a page
                return f"PAGE:{page['id']}"
        except Exception as page_error:
            # If it's not a page either, it's an invalid URL
            raise NotionError(f"Invalid URL: {notion_url} - Could not retrieve as database or page") from page_error
            
    except NotionError:
        # Re-raise NotionError as-is
        raise
    except Exception as e:
        raise NotionError(f"Invalid URL: {e}") from e


def create_database_in_page(
    client: NotionClient,
    page_id: str,
    database_name: str,
    csv_data: LocalData,
    skip_columns: Optional[List[str]] = None,
) -> Tuple[str, str]:
    """
    Create a database within an existing page using official API.
    
    Args:
        client: Official Notion client
        page_id: ID of the page to create database in
        database_name: Name for the new database
        csv_data: CSV data to determine schema
        skip_columns: Columns to skip
        
    Returns:
        Tuple of (database_url, database_id)
    """
    try:
        # Create database schema from CSV data
        schema = _schema_from_csv(csv_data, skip_columns)
        
        # Create database within the specified page using the wrapper method
        database = client.create_database(
            parent_page_id=page_id,
            title=database_name,
            properties=schema
        )
        
        return database["url"], database["id"]
        
    except Exception as e:
        raise NotionError(f"Failed to create database in page: {e}") from e


def notion_db_from_csv(
    client: NotionClient,
    page_name: str,
    csv_data: LocalData,
    skip_columns: Optional[List[str]] = None,
) -> Tuple[str, str]:
    """
    Create a database from CSV data using official API.
    
    Args:
        client: Official Notion client
        page_name: Database name
        csv_data: CSV data
        skip_columns: Columns to skip
        
    Returns:
        Tuple of (database_url, database_id)
    """
    try:
        # Create parent page first
        parent_page = client.create_page(
            parent={"type": "page_id", "page_id": client.current_user["id"]},
            properties={"title": [{"text": {"content": page_name}}]}
        )
        parent_page_id = parent_page["id"]
        
        # Create database schema
        schema = _schema_from_csv(csv_data, skip_columns)
        
        # Create database
        database = client.create_database(
            parent_page_id=parent_page_id,
            title=page_name,
            properties=schema
        )
        
        return database["url"], database["id"]
        
    except Exception as e:
        raise NotionError(f"Failed to create database from CSV: {e}") from e


def _schema_from_csv(
    csv_data: LocalData, skip_columns: Optional[List[str]] = None
) -> Dict[str, Dict[str, Any]]:
    """Create database schema from CSV data."""
    # Get all columns and ensure key column is first
    all_columns = csv_data.columns
    key_column = csv_data.key_column
    
    # Create ordered list with key column first, then all other columns
    if key_column in all_columns:
        other_columns = [c for c in all_columns if c != key_column]
        columns = [key_column] + other_columns
    else:
        columns = all_columns
    
    # Apply skip_columns filter
    if skip_columns:
        columns = [c for c in columns if c not in skip_columns]
    
    # Create schema starting with title property using the key column
    schema = {}
    
    for i, col_key in enumerate(columns):
        # Key column becomes the title property
        if col_key == key_column:
            schema[col_key] = {"title": {}}
        else:
            # Get column type for non-key columns
            try:
                col_type = csv_data.col_type(col_key)
                # Log that we're using pre-defined column type
                # import logging
                # logging.getLogger(__name__).debug(f"Using pre-defined type '{col_type}' for column '{col_key}'")
            except KeyError:
                # If column type not found, analyze the data to determine type
                col_type = _analyze_column_type(csv_data, col_key)
                # Log the auto-detected type
                # import logging
                # logging.getLogger(__name__).debug(f"Auto-detected type '{col_type}' for column '{col_key}'")
            
            # Create property based on detected type
            if col_type == "status":
                schema[col_key] = {"status": make_status_column()}
            elif col_type == "select":
                schema[col_key] = {"select": {"options": []}}
            elif col_type == "multi_select":
                schema[col_key] = {"multi_select": {"options": []}}
            elif col_type == "checkbox":
                schema[col_key] = {"checkbox": {}}
            elif col_type == "number":
                schema[col_key] = {"number": {}}
            elif col_type == "url":
                schema[col_key] = {"url": {}}
            elif col_type == "email":
                schema[col_key] = {"email": {}}
            elif col_type == "phone_number":
                schema[col_key] = {"phone_number": {}}
            elif col_type == "date":
                schema[col_key] = {"date": {}}
            else:
                # Default to rich_text for all other types
                schema[col_key] = {"rich_text": {}}
    
    return schema


def _analyze_column_type(csv_data: LocalData, col_key: str) -> str:
    """Advanced column type detection with smart pattern recognition."""
    import re
    from datetime import datetime
    from decimal import Decimal, InvalidOperation
    
    try:
        values = csv_data.col_values(col_key)
        if not values:
            return "rich_text"
        
        # Filter out None, empty strings, and whitespace-only values
        clean_values = [str(v).strip() for v in values if v is not None and str(v).strip()]
        if not clean_values:
            return "rich_text"
        
        # Check for multi_select (array values)
        if any(isinstance(v, list) for v in values):
            return "multi_select"
        
        # 1. TIME CODE DETECTION (like "00:00:08:06", "00:00:22:07")
        timecode_pattern = r'^\d{2}:\d{2}:\d{2}:\d{2}$'
        if any(re.match(timecode_pattern, v) for v in clean_values):
            return "rich_text"  # Timecode should be rich text as requested
        
        # 2. BOOLEAN/CHECKBOX DETECTION
        boolean_patterns = {
            'true', 'false', 'yes', 'no', 'on', 'off', 'enabled', 'disabled',
            'complete', 'incomplete', 'done', 'pending', 'active', 'inactive',
            '1', '0', 'y', 'n', 't', 'f'
        }
        boolean_like = sum(1 for v in clean_values if v.lower() in boolean_patterns)
        if boolean_like >= len(clean_values) * 0.8:  # 80% match boolean patterns
            return "checkbox"
        
        # 3. STATUS/SELECT DETECTION (limited unique values with semantic meaning)
        unique_values = set(clean_values)
        if 2 <= len(unique_values) <= 10:  # Good range for select/status
            # Check if values look like status options
            status_indicators = {'complete', 'incomplete', 'pending', 'done', 'todo', 'active', 'inactive'}
            if any(v.lower() in status_indicators for v in unique_values):
                return "select"
            
            # Check if values are short and meaningful (not just numbers)
            if all(len(v) <= 30 and not v.replace(".", "").replace("-", "").isdigit() for v in unique_values):
                return "select"
        
        # 4. NUMERIC DETECTION (integers, decimals, percentages)
        numeric_count = 0
        for v in clean_values:
            try:
                # Try to parse as number (handles integers, decimals, scientific notation)
                float(v.replace(',', '').replace('%', ''))
                numeric_count += 1
            except (ValueError, InvalidOperation):
                pass
        
        if numeric_count >= len(clean_values) * 0.8:  # 80% are numeric
            return "number"
        
        # 5. URL DETECTION
        url_pattern = r'^https?://[^\s]+$'
        if any(re.match(url_pattern, v) for v in clean_values):
            return "url"
        
        # 6. EMAIL DETECTION
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if any(re.match(email_pattern, v) for v in clean_values):
            return "email"
        
        # 7. PHONE NUMBER DETECTION
        phone_pattern = r'^[\+]?[1-9][\d\s\-\(\)]{7,15}$'
        if any(re.match(phone_pattern, v) for v in clean_values):
            return "phone_number"
        
        # 8. DATE DETECTION (various formats)
        date_patterns = [
            r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
            r'^\d{2}/\d{2}/\d{4}$',   # MM/DD/YYYY
            r'^\d{2}-\d{2}-\d{4}$',  # MM-DD-YYYY
            r'^\d{4}/\d{2}/\d{2}$',  # YYYY/MM/DD
            r'^\d{1,2}/\d{1,2}/\d{4}$',  # M/D/YYYY
        ]
        
        date_count = 0
        for v in clean_values:
            for pattern in date_patterns:
                if re.match(pattern, v):
                    try:
                        # Try to parse as date to validate
                        datetime.strptime(v, '%Y-%m-%d')
                        date_count += 1
                        break
                    except ValueError:
                        try:
                            datetime.strptime(v, '%m/%d/%Y')
                            date_count += 1
                            break
                        except ValueError:
                            try:
                                datetime.strptime(v, '%m-%d-%Y')
                                date_count += 1
                                break
                            except ValueError:
                                try:
                                    datetime.strptime(v, '%Y/%m/%d')
                                    date_count += 1
                                    break
                                except ValueError:
                                    try:
                                        datetime.strptime(v, '%m/%d/%Y')
                                        date_count += 1
                                        break
                                    except ValueError:
                                        pass
        
        if date_count >= len(clean_values) * 0.7:  # 70% are valid dates
            return "date"
        
        # 9. MULTI-SELECT DETECTION (comma-separated values)
        if any(',' in v for v in clean_values):
            # Check if values look like multi-select options
            multi_select_candidates = [v for v in clean_values if ',' in v]
            if len(multi_select_candidates) >= len(clean_values) * 0.5:  # 50% have commas
                return "multi_select"
        
        # 10. RICH TEXT DETECTION (long text, descriptions, mixed content)
        # If values are long or contain mixed content, default to rich text
        avg_length = sum(len(v) for v in clean_values) / len(clean_values)
        if avg_length > 50:  # Average length > 50 characters
            return "rich_text"
        
        # Default to rich_text for any unclassified content
        return "rich_text"
        
    except Exception as e:
        # Log the error for debugging but don't fail
        import logging
        logging.getLogger(__name__).warning(f"Error analyzing column type for {col_key}: {e}")
        return "rich_text"


def get_notion_client(
    integration_token: str, 
    workspace: Optional[str] = None, 
    **options
) -> NotionClient:
    """
    Factory function to create official Notion client.
    
    Args:
        integration_token: Notion integration token
        workspace: Workspace name (for compatibility)
        **options: Additional options
        
    Returns:
        NotionClient instance
    """
    from csv2notion_neo.notion_client import get_notion_client as get_client
    return get_client(integration_token, workspace, **options)
