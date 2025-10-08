"""
Official Notion SDK File Upload Operations for CSV2Notion Neo

This module provides file upload operations using the official Notion SDK,
maintaining compatibility with the existing CSV2Notion Neo codebase.
"""

import mimetypes
import re
from pathlib import Path
from typing import Dict, Optional, Tuple

from csv2notion_neo.notion_client import NotionClient
from csv2notion_neo.utils_exceptions import NotionError
from csv2notion_neo.utils_file import get_file_sha256
from csv2notion_neo.utils_static import FileType

Meta = Dict[str, str]


def upload_filetype(
    client: NotionClient, 
    filetype: FileType
) -> Tuple[str, Meta]:
    """
    Upload a file using the official Notion API.
    
    Args:
        client: Official Notion client
        filetype: File to upload (Path or URL)
        
    Returns:
        Tuple of (file_url, metadata)
    """
    if isinstance(filetype, Path):
        url, meta = upload_file(client, filetype)
    else:
        url = filetype
        meta = {"source": [[url]]}
    
    return url, meta


def upload_file(
    client: NotionClient, 
    file_path: Path
) -> Tuple[str, Meta]:
    """
    Upload a file using the official Notion API.
    
    Args:
        client: Official Notion client
        file_path: Path to file to upload
        
    Returns:
        Tuple of (file_url, metadata)
    """
    try:
        # Use the official client's upload method
        file_url, metadata = client.upload_file(file_path, "")
        
        return file_url, metadata
        
    except Exception as e:
        raise NotionError(f"Could not upload file {file_path}: {e}") from e


def get_file_id(image_url: str) -> Optional[str]:
    """
    Extract file ID from image URL.
    
    Args:
        image_url: Image URL
        
    Returns:
        File ID or None
    """
    # Pattern: attachment:file_id:filename
    attachment_re = r"^attachment:([a-f0-9\-]+):(.+)$"
    aws_match = re.search(attachment_re, image_url)
    
    if aws_match:
        return aws_match.group(1)
    
    return None


def is_meta_different(
    image: Optional[FileType],
    image_url: Optional[str],
    image_meta: Optional[Meta],
) -> bool:
    """
    Check if image metadata is different.
    
    Args:
        image: Image file or URL
        image_url: Current image URL
        image_meta: Current image metadata
        
    Returns:
        True if metadata is different
    """
    if not all([image_meta, image_url, image]):
        return True
    
    if isinstance(image, Path) and image_url is not None and image_meta is not None:
        return _is_file_meta_different(image, image_url, image_meta)
    elif image_meta != {"type": "url", "url": image}:
        return True
    
    return False


def _is_file_meta_different(
    image: Path, 
    image_url: str, 
    image_meta: Meta
) -> bool:
    """
    Check if file metadata is different.
    
    Args:
        image: Image file path
        image_url: Current image URL
        image_meta: Current image metadata
        
    Returns:
        True if metadata is different
    """
    if image_meta.get("type") != "file":
        return True
    
    if image_meta.get("file_id") != get_file_id(image_url):
        return True
    
    return image_meta.get("sha256") != get_file_sha256(image)


def create_file_upload(
    client: NotionClient,
    filename: str,
    content_type: Optional[str] = None,
    file_size: Optional[int] = None
) -> str:
    """
    Create a file upload using the official API.
    
    Args:
        client: Official Notion client
        filename: Name of the file
        content_type: MIME content type
        file_size: Size of the file in bytes
        
    Returns:
        File upload ID
    """
    try:
        # Determine upload mode based on file size
        if file_size and file_size > 20 * 1024 * 1024:  # 20MB
            mode = "multi_part"
        else:
            mode = "single_part"
        
        # Create file upload
        response = client.client.file_uploads.create(
            mode=mode,
            filename=filename,
            content_type=content_type or "application/octet-stream"
        )
        
        return response["id"]
        
    except Exception as e:
        raise NotionError(f"Failed to create file upload: {e}") from e


def send_file_upload(
    client: NotionClient,
    file_upload_id: str,
    file_path: Path
) -> Dict[str, any]:
    """
    Send file data to the upload.
    
    Args:
        client: Official Notion client
        file_upload_id: File upload ID
        file_path: Path to file to upload
        
    Returns:
        Upload response
    """
    try:
        with open(file_path, "rb") as f:
            response = client.client.file_uploads.send(
                file_upload_id=file_upload_id,
                file=f
            )
        
        return response
        
    except Exception as e:
        raise NotionError(f"Failed to send file upload: {e}") from e


def complete_file_upload(
    client: NotionClient,
    file_upload_id: str
) -> Dict[str, any]:
    """
    Complete the file upload process.
    
    Args:
        client: Official Notion client
        file_upload_id: File upload ID
        
    Returns:
        Completion response
    """
    try:
        response = client.client.file_uploads.complete(file_upload_id=file_upload_id)
        return response
        
    except Exception as e:
        raise NotionError(f"Failed to complete file upload: {e}") from e


def get_content_type(file_path: Path) -> str:
    """
    Get content type for file.
    
    Args:
        file_path: Path to file
        
    Returns:
        MIME content type
    """
    content_type, _ = mimetypes.guess_type(str(file_path))
    return content_type or "application/octet-stream"


def upload_file_with_retry(
    client: NotionClient,
    file_path: Path,
    max_retries: int = 3
) -> Tuple[str, Meta]:
    """
    Upload file with retry logic.
    
    Args:
        client: Official Notion client
        file_path: Path to file to upload
        max_retries: Maximum number of retries
        
    Returns:
        Tuple of (file_url, metadata)
    """
    last_error = None
    
    for attempt in range(max_retries):
        try:
            return upload_file(client, file_path)
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                # Wait before retry (exponential backoff)
                import time
                time.sleep(2 ** attempt)
            continue
    
    raise NotionError(f"Failed to upload file {file_path} after {max_retries} attempts: {last_error}")


def validate_file_for_upload(file_path: Path) -> None:
    """
    Validate file for upload.
    
    Args:
        file_path: Path to file to validate
        
    Raises:
        NotionError: If file is invalid
    """
    if not file_path.exists():
        raise NotionError(f"File does not exist: {file_path}")
    
    if not file_path.is_file():
        raise NotionError(f"Path is not a file: {file_path}")
    
    # Check file size (100MB limit for multi-part uploads)
    file_size = file_path.stat().st_size
    if file_size > 100 * 1024 * 1024:  # 100MB
        raise NotionError(f"File size {file_size} exceeds 100MB limit")
    
    if file_size == 0:
        raise NotionError(f"File is empty: {file_path}")


def get_file_upload_status(
    client: NotionClient,
    file_upload_id: str
) -> Dict[str, any]:
    """
    Get file upload status.
    
    Args:
        client: Official Notion client
        file_upload_id: File upload ID
        
    Returns:
        Upload status response
    """
    try:
        response = client.client.file_uploads.retrieve(file_upload_id=file_upload_id)
        return response
        
    except Exception as e:
        raise NotionError(f"Failed to get file upload status: {e}") from e
