"""
Official Notion SDK Database Operations for CSV2Notion Neo

This module provides database operations using the official Notion SDK,
maintaining compatibility with the existing CSV2Notion Neo codebase.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from csv2notion_neo.notion_client_official import NotionClientOfficial
from csv2notion_neo.local_data import LocalData
from csv2notion_neo.utils_exceptions import NotionError
from csv2notion_neo.utils_rand_id import rand_id_list
from csv2notion_neo.utils_db import make_status_column

logger = logging.getLogger(__name__)


class NotionDBOfficial:
    """
    Official Notion SDK database operations adapter.
    Maintains compatibility with existing NotionDB interface.
    """
    
    def __init__(self, client: NotionClientOfficial, collection_id: str):
        """
        Initialize database operations.
        
        Args:
            client: Official Notion client
            collection_id: Database/collection ID
        """
        self.client = client
        self.collection_id = collection_id
        self.logger = logging.getLogger(__name__)
        
        # Cache for performance
        self._cache_columns: Optional[Dict[str, Dict[str, str]]] = None
        self._cache_relations: Optional[Dict[str, "NotionDBOfficial"]] = None
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
    def relations(self) -> Dict[str, "NotionDBOfficial"]:
        """Get related databases."""
        if self._cache_relations is None:
            self._cache_relations = {}
            
            for col_name, col_data in self.columns.items():
                if col_data["type"] == "relation":
                    collection_id = col_data.get("collection_id")
                    if collection_id:
                        self._cache_relations[col_name] = NotionDBOfficial(
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
    
    def add_row(
        self,
        properties: Optional[Dict[str, Any]] = None,
        columns: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Add a row to the database."""
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
            
            # Update cache
            if columns and self.key_column in columns:
                key_value = columns[self.key_column]
                self._cache_rows[key_value] = response
            
            return response
            
        except Exception as e:
            raise NotionError(f"Failed to add row: {e}") from e
    
    def add_row_key(self, key: str) -> Dict[str, Any]:
        """Add a row with just a key value."""
        return self.add_row(columns={self.key_column: key})
    
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
                    logger.warning(f"Select option '{value}' not found in database schema for property '{prop_name}'. Available options: {option_names}. Skipping property.")
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
                    valid_values = [str(v) for v in value if v and str(v) in option_names]
                    invalid_values = [str(v) for v in value if v and str(v) not in option_names]
                    if invalid_values:
                        logger.warning(f"Multi-select options {invalid_values} not found in database schema for property '{prop_name}'. Available options: {option_names}. Skipping invalid options.")
                    return {"multi_select": [{"name": v} for v in valid_values]}
                else:
                    if str(value) not in option_names:
                        logger.warning(f"Multi-select option '{value}' not found in database schema for property '{prop_name}'. Available options: {option_names}. Skipping property.")
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
            return {"date": {"start": str(value)}}
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
                    logger.warning(f"Status option '{value}' not found in database schema for property '{prop_name}'. Available options: {option_names}. Skipping property.")
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


def get_collection_id_official(client: NotionClientOfficial, notion_url: str) -> str:
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
                # For now, we'll raise an error with a helpful message
                raise NotionError(
                    f"Page URL provided: {notion_url}\n"
                    f"CSV2Notion Neo requires a database URL, not a page URL.\n"
                    f"Please provide the URL of an existing Notion database, or create a new database first."
                )
        except Exception as page_error:
            # If it's not a page either, it's an invalid URL
            raise NotionError(f"Invalid URL: {notion_url} - Could not retrieve as database or page") from page_error
            
    except NotionError:
        # Re-raise NotionError as-is
        raise
    except Exception as e:
        raise NotionError(f"Invalid URL: {e}") from e


def notion_db_from_csv_official(
    client: NotionClientOfficial,
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
        schema = _schema_from_csv_official(csv_data, skip_columns)
        
        # Create database
        database = client.create_database(
            parent_page_id=parent_page_id,
            title=page_name,
            properties=schema
        )
        
        return database["url"], database["id"]
        
    except Exception as e:
        raise NotionError(f"Failed to create database from CSV: {e}") from e


def _schema_from_csv_official(
    csv_data: LocalData, skip_columns: Optional[List[str]] = None
) -> Dict[str, Dict[str, Any]]:
    """Create database schema from CSV data."""
    if skip_columns:
        columns = [c for c in csv_data.content_columns if c not in skip_columns]
    else:
        columns = csv_data.content_columns
    
    schema_ids = rand_id_list(len(columns), 4)
    
    schema = {"title": {"name": csv_data.key_column, "type": "title"}}
    
    for col_id, col_key in zip(schema_ids, columns):
        col_type = csv_data.col_type(col_key)
        schema[col_id] = {
            "name": col_key,
            "type": col_type,
        }
        
        if col_type == "status":
            schema[col_id].update(make_status_column())
    
    return schema


def get_notion_client_official(
    integration_token: str, 
    workspace: Optional[str] = None, 
    **options
) -> NotionClientOfficial:
    """
    Factory function to create official Notion client.
    
    Args:
        integration_token: Notion integration token
        workspace: Workspace name (for compatibility)
        **options: Additional options
        
    Returns:
        NotionClientOfficial instance
    """
    from csv2notion_neo.notion_client_official import get_notion_client_official as get_client
    return get_client(integration_token, workspace, **options)
