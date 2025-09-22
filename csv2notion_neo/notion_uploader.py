import logging
from dataclasses import dataclass
from typing import Any, Dict

from csv2notion_neo.notion_db_official import NotionDBOfficial
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
    def __init__(self, db: NotionDBOfficial):
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

        existing_row = self.db.rows.get(row.key()) if is_merge else None

        if is_merge and existing_row:
            # Update existing row
            page_id = existing_row.get("id")
            if page_id:
                cur_row = self.db.update_row(page_id, properties=row.properties, columns=row.columns)
            else:
                # Fallback to creating new row if no page ID found
                cur_row = self.db.add_row(properties=row.properties, columns=row.columns)
        else:
            cur_row = self.db.add_row(properties=row.properties, columns=row.columns)
        return cur_row

    def _process_image_uploads(self, db_row: Dict[str, Any], post_properties: Dict[str, Any]) -> None:
        """Process image uploads using the official Notion API."""
        from pathlib import Path
        from csv2notion_neo.notion_row_upload_file_official import upload_filetype_official
        
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
                                image_url, metadata = upload_filetype_official(self.db.client, image)
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
                        cover_url, metadata = upload_filetype_official(self.db.client, cover_image)
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
                        icon_url, metadata = upload_filetype_official(self.db.client, icon)
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
