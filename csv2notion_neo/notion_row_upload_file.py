import mimetypes
import re
from pathlib import Path
from typing import Dict, Optional, Tuple

import requests
from csv2notion_neo.notion_client_official import NotionClientOfficial

from csv2notion_neo.utils_exceptions import NotionError
from csv2notion_neo.utils_file import get_file_sha256
from csv2notion_neo.utils_static import FileType
from urllib.parse import urlparse
from icecream import ic

Meta = Dict[str, str]


def upload_filetype(parent: NotionClientOfficial, filetype: FileType) -> Tuple[str, Meta]:

    if isinstance(filetype, Path):
        url, meta = upload_file(parent, filetype)
    else:
        url = filetype
        meta = {"source": [[url]]}

    return url, meta


def upload_file(block: NotionClientOfficial, file_path: Path) -> Tuple[str, Meta]:

    file_url = _upload_file(block, file_path)

    file_id = get_file_id(file_url)

    if file_id is None:
        raise NotionError(f"Could not upload file {file_path}")

    return file_url, {"source": [[file_url]]}
    # return file_url, {
    #     "type": "file",
    #     "file_id": file_id,
    #     "sha256": get_file_sha256(file_path),
    # }


def _upload_file(block: NotionClientOfficial, file_path: Path) -> str:
    """Upload file using official Notion API."""
    try:
        # Use the official client's upload method
        file_url, metadata = block.upload_file(file_path, "")
        return file_url
    except Exception as e:
        raise NotionError(f"Failed to upload file {file_path}: {e}") from e


def get_file_id(image_url: str) -> Optional[str]:

    # aws_host/space_id/file_id/filename
    # aws_re = r"^https://(.*?\.amazonaws\.com)/([a-f0-9\-]+)/([a-f0-9\-]+)/(.*?)$"
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
    if not all([image_meta, image_url, image]):
        return True

    if isinstance(image, Path) and image_url is not None and image_meta is not None:
        return _is_file_meta_different(image, image_url, image_meta)

    elif image_meta != {"type": "url", "url": image}:
        return True

    return False


def _is_file_meta_different(image: Path, image_url: str, image_meta: Meta) -> bool:
    if image_meta["type"] != "file":
        return True

    if image_meta["file_id"] != get_file_id(image_url):
        return True

    return image_meta["sha256"] != get_file_sha256(image)
