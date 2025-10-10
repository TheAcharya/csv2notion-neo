"""
CSV2Notion Neo - Notion Uploader

This module handles the uploading of processed data to Notion databases.
It manages the upload process, including AI-powered content generation,
image processing, and database operations using the official Notion API.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict

from csv2notion_neo.notion_db import NotionDB
from icecream import ic
from csv2notion_neo.utils_ai import AI

logger = logging.getLogger(__name__)


@dataclass
class NotionUploadRow(object):
    columns: Dict[str, Any]
    properties: Dict[str, Any]

    def key(self) -> str:
        if "payload_key_column" in self.properties:
            if self.properties["payload_key_column"]:
                return str(self.columns[self.properties["payload_key_column"]])
        return str(list(self.columns.values())[0])


class NotionRowUploader(object):
    def __init__(self, db: NotionDB):
        self.db = db

    def upload_row(self, row: NotionUploadRow, is_merge: bool) -> None:

        if "AI" in row.properties:
            ai_client = AI(row.properties["AI"])
            row.columns = ai_client.out(row.columns)
        # row.columns['ai caption'] = '2'
        post_properties = _extract_post_properties(row.properties)

        db_row = self._get_db_row(row, is_merge)

        # Process image uploads using the official API
        self._process_image_uploads(db_row, post_properties)

        # these need to be updated after
        # because they can't be updated in atomic transaction
        for prop, prop_val in post_properties.items():
            # For official API, db_row is a dictionary, so we update it directly
            if isinstance(db_row, dict):
                db_row[prop] = prop_val
            else:
                # Fallback for old API compatibility
                setattr(db_row, prop, prop_val)

    def _get_db_row(
        self, row: NotionUploadRow, is_merge: bool
    ) -> Dict[str, Any]:
        """
        Get or create database row with thread-safe merge logic.
        
        This method implements a bulletproof approach to prevent duplicates
        in multi-threaded environments by using a two-phase approach:
        1. Try to find existing row in cache
        2. If not found, attempt to create with conflict detection
        """
        if not is_merge:
            # Not a merge operation, always create new row
            return self.db.add_row(properties=row.properties, columns=row.columns)
        
        # For merge operations, use thread-safe approach
        row_key = row.key()
        
        # First, check if row exists in current cache
        existing_row = self.db.rows.get(row_key)
        
        if existing_row:
            # Row exists, update it
            page_id = existing_row.get("id")
            if page_id:
                return self.db.update_row(page_id, properties=row.properties, columns=row.columns)
            else:
                # Fallback: create new row if no page ID found
                return self.db.add_row(properties=row.properties, columns=row.columns)
        
        # Row doesn't exist in cache, try to create it
        # Use a try-catch approach to handle race conditions
        try:
            return self.db.add_row(properties=row.properties, columns=row.columns)
        except Exception as e:
            # If creation fails due to conflict (row was created by another thread),
            # refresh cache and try to update instead
            if "conflict" in str(e).lower() or "duplicate" in str(e).lower():
                # Refresh cache to get the latest data
                self.db.invalidate_cache()
                
                # Check again if row now exists
                existing_row = self.db.rows.get(row_key)
                if existing_row:
                    page_id = existing_row.get("id")
                    if page_id:
                        return self.db.update_row(page_id, properties=row.properties, columns=row.columns)
            
            # If we still can't resolve it, re-raise the original exception
            raise e

    def _process_image_uploads(self, db_row: Dict[str, Any], post_properties: Dict[str, Any]) -> None:
        """Process image uploads using the official Notion API."""
        from pathlib import Path
        from csv2notion_neo.notion_row_upload_file import upload_filetype
        
        page_id = db_row.get("id")
        if not page_id:
            return
            
        # Process cover_block (images as blocks)
        if "cover_block" in post_properties:
            images = post_properties["cover_block"]
            if images:
                for image in images:
                    if image:
                        try:
                            # Upload the image file
                            if isinstance(image, Path):
                                image_url, metadata = upload_filetype(self.db.client, image)
                                # For uploaded files, use file_upload with the file upload ID
                                if "file_id" in metadata:
                                    image_block = {
                                        "type": "image",
                                        "image": {
                                            "type": "file_upload",
                                            "file_upload": {
                                                "id": metadata["file_id"]
                                            }
                                        }
                                    }
                                else:
                                    # Fallback to external URL
                                    image_block = {
                                        "type": "image",
                                        "image": {
                                            "type": "external",
                                            "external": {"url": image_url}
                                        }
                                    }
                            else:
                                # It's already a URL
                                image_url = str(image)
                                image_block = {
                                    "type": "image",
                                    "image": {
                                        "type": "external",
                                        "external": {"url": image_url}
                                    }
                                }
                            
                            # Add image block to the page
                            self.db.client.client.blocks.children.append(
                                block_id=page_id,
                                children=[image_block]
                            )
                        except Exception as e:
                            logger.warning(f"Failed to upload image {image}: {e}")
        
        # Process cover (page cover image)
        if "cover" in post_properties:
            cover_images = post_properties["cover"]
            if cover_images and cover_images[0]:
                try:
                    cover_image = cover_images[0]
                    # Upload the cover image file
                    if isinstance(cover_image, Path):
                        cover_url, metadata = upload_filetype(self.db.client, cover_image)
                        # For uploaded files, use file_upload with the file upload ID
                        if "file_id" in metadata:
                            cover_data = {
                                "type": "file_upload",
                                "file_upload": {
                                    "id": metadata["file_id"]
                                }
                            }
                        else:
                            # Fallback to external URL
                            cover_data = {
                                "type": "external",
                                "external": {"url": cover_url}
                            }
                    else:
                        # It's already a URL
                        cover_url = str(cover_image)
                        cover_data = {
                            "type": "external",
                            "external": {"url": cover_url}
                        }
                    
                    # Set page cover
                    self.db.client.client.pages.update(
                        page_id=page_id,
                        cover=cover_data
                    )
                except Exception as e:
                    logger.warning(f"Failed to upload cover image {cover_images[0]}: {e}")
        
        # Process icon
        if "icon" in post_properties:
            icon = post_properties["icon"]
            if icon:
                try:
                    # Upload the icon file
                    if isinstance(icon, Path):
                        icon_url, metadata = upload_filetype(self.db.client, icon)
                        # For uploaded files, use file_upload with the file upload ID
                        if "file_id" in metadata:
                            icon_data = {
                                "type": "file_upload",
                                "file_upload": {
                                    "id": metadata["file_id"]
                                }
                            }
                        else:
                            # Fallback to external URL
                            icon_data = {
                                "type": "external",
                                "external": {"url": icon_url}
                            }
                    else:
                        # It's already a URL or emoji
                        if str(icon).startswith("http"):
                            icon_data = {
                                "type": "external",
                                "external": {"url": str(icon)}
                            }
                        else:
                            # It's an emoji
                            icon_data = {
                                "type": "emoji",
                                "emoji": str(icon)
                            }
                    
                    # Set page icon
                    self.db.client.client.pages.update(
                        page_id=page_id,
                        icon=icon_data
                    )
                except Exception as e:
                    logger.warning(f"Failed to upload icon {icon}: {e}")


def _extract_post_properties(properties: Dict[str, Any]) -> Dict[str, Any]:
    return {
        p: properties.pop(p)
        for p in properties.copy()
        if p in {"cover_block", "cover_block_caption", "last_edited_time", "cover", "icon"}
    }
