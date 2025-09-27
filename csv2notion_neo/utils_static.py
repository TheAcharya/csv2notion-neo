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
