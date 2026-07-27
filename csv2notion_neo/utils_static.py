"""
CSV2Notion Neo - Static Configuration and Types

This module provides static configuration constants, type definitions,
and the ConversionRules dataclass for managing CSV2Notion Neo application
settings and data conversion parameters.
"""

from argparse import Namespace
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Union
from urllib.parse import urlparse

# Notion app hosts after the June 2026 migration from notion.so → notion.com.
# Existing notion.so links continue to work; API-generated links use app.notion.com.
# Include app.notion.so for transitional/legacy bookmarks during the migration.
# Keep this allowlist explicit so docs hosts (e.g. developers.notion.com) are rejected.
ALLOWED_NOTION_HOSTS = frozenset(
    (
        "notion.so",
        "www.notion.so",
        "app.notion.so",
        "notion.com",
        "www.notion.com",
        "app.notion.com",
    )
)

# NOTE:
# "relation" is intentionally excluded from ALLOWED_TYPES used by --column-types.
# Unlike scalar property types, relation columns require additional Notion metadata
# (target database/data source linkage). The current --column-types flow only
# accepts plain type names and cannot safely create relation schema from that
# alone. Relation values are supported when the relation column already exists in
# the target database.
ALLOWED_TYPES = frozenset(
    (
        "checkbox",
        "date",
        "multi_select",
        "status",
        "select",
        "number",
        "email",
        "phone_number",
        "url",
        "text",
        "created_time",
        "last_edited_time",
        "created_by",
        "last_edited_by",
        "rollup",
        "formula",
        "file",
        "person",
    )
)

UNSETTABLE_TYPES = frozenset(("created_by", "last_edited_by", "rollup", "formula"))

FileType = Union[str, Path]


def is_notion_hostname(hostname: Optional[str]) -> bool:
    """Return True if hostname is a first-party Notion app host (.so or .com)."""
    if not hostname:
        return False
    return hostname.lower().rstrip(".") in ALLOWED_NOTION_HOSTS


def is_notion_url(url: str) -> bool:
    """Return True if url is an http(s) link on an allowed Notion app host."""
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    if parsed.scheme not in {"http", "https"}:
        return False
    return is_notion_hostname(parsed.hostname)


@dataclass
class ConversionRules(object):
    csv_file: Path

    # Core CLI arguments
    token: str
    url: str
    workspace: str
    max_threads: int
    verbose: bool
    log: Optional[Path]
    
    # File processing arguments
    column_types: Optional[Dict[str, str]]
    delimiter: str
    fail_on_duplicate_csv_columns: bool
    randomize_select_colors: bool

    # Image and icon columns
    image_column: Optional[List[str]]
    image_column_keep: bool
    image_column_mode: str
    image_caption_column: Optional[str]
    image_caption_column_keep: bool

    icon_column: Optional[str]
    icon_column_keep: bool
    default_icon: Optional[FileType]

    # Merge operations
    merge: bool
    merge_only_column: List[str]
    merge_skip_new: bool

    # Database schema management
    add_missing_columns: bool
    add_missing_relations: bool

    # Validation and error handling
    mandatory_column: List[str]
    fail_on_relation_duplicates: bool
    fail_on_duplicates: bool
    fail_on_conversion_error: bool
    fail_on_inaccessible_relations: bool
    fail_on_missing_columns: bool
    fail_on_unsettable_columns: bool
    fail_on_wrong_status_values: bool

    # Column mapping and data processing
    rename_notion_key_column: Optional[List[str]]
    payload_key_column: Optional[str]

    # AI and advanced features
    hugging_face_token: Optional[str]
    caption_column: Optional[List[str]]
    hf_model: Optional[str]
    
    # Database operations
    delete_all_database_entries: bool

    @property
    def files_search_path(self) -> Path:
        return self.csv_file.parent

    @classmethod
    def from_args(cls, args: Namespace) -> "ConversionRules":
        args_map = {
            arg_name: getattr(args, arg_name) for arg_name in cls.__dataclass_fields__
        }

        return cls(**args_map)
