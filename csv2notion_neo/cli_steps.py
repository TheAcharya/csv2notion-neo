"""
CSV2Notion Neo - CLI Workflow Steps

This module provides the main workflow steps invoked by the CLI: database deletion,
new database creation from CSV, conversion of CSV/JSON rows to Notion format, and
upload of rows (single- or multi-threaded) with progress reporting.
"""

import logging
from argparse import Namespace
from functools import partial
from typing import List
from icecream import ic

from tqdm import tqdm

from csv2notion_neo.local_data import LocalData
from csv2notion_neo.notion_convert import NotionRowConverter
from csv2notion_neo.notion_db import NotionDB, notion_db_from_csv
from csv2notion_neo.notion_client import NotionClient
from csv2notion_neo.notion_preparator import NotionPreparator
from csv2notion_neo.notion_uploader import NotionUploadRow
from csv2notion_neo.utils_static import ConversionRules
from csv2notion_neo.utils_threading import ThreadRowUploader, process_iter

logger = logging.getLogger(__name__)


def delete_all_database_entries(
    client: NotionClient, collection_id: str
) -> int:
    """
    Delete all entries from a Notion database.
    
    Args:
        client: Official Notion client
        collection_id: Database ID
        
    Returns:
        Number of entries deleted
    """
    logger.info("Starting deletion of all database entries...")
    
    notion_db = NotionDB(client, collection_id)
    deleted_count = notion_db.delete_all_entries()
    
    return deleted_count


def new_database(
    args: Namespace, client: NotionClient, csv_data: LocalData
) -> str:
    skip_columns = []
    if args.image_column and not args.image_column_keep:
        skip_columns.append(args.image_column)
    if args.icon_column and not args.icon_column_keep:
        skip_columns.append(args.icon_column)
    if args.image_caption_column and not args.image_caption_column_keep:
        skip_columns.append(args.image_caption_column)

    logger.info("Creating new database")

    url, collection_id = notion_db_from_csv(
        client,
        page_name=args.csv_file.stem,
        csv_data=csv_data,
        skip_columns=skip_columns,
    )

    logger.info(f"New database URL: {url}")

    return url


def convert_csv_to_notion_rows(
    csv_data: LocalData,
    client: NotionClient,
    collection_id: str,
    args: Namespace,
) -> List[NotionUploadRow]:
    notion_db = NotionDB(client, collection_id)

    conversion_rules = ConversionRules.from_args(args)

    NotionPreparator(notion_db, csv_data, conversion_rules).prepare()

    converter = NotionRowConverter(notion_db, conversion_rules)

    return converter.convert_to_notion_rows(csv_data)


def upload_rows(
    notion_rows: List[NotionUploadRow],
    client: NotionClient,
    collection_id: str,
    is_merge: bool,
    max_threads: int,
) -> None:
    # Create progress bar with real-time updates but same look as before
    with tqdm(
        total=len(notion_rows),
        leave=False,
        mininterval=0.1,  # Update at least every 100ms for real-time updates
        maxinterval=1.0,   # Update at most every 1 second
        smoothing=0.1,     # Smooth progress updates
    ) as pbar:
        
        if max_threads == 1:
            # Single-threaded: update progress bar during each operation
            worker = partial(
                ThreadRowUploader(client, collection_id).worker,
                is_merge=is_merge,
            )
            for i, row in enumerate(notion_rows):
                worker(row)
                pbar.update(1)
                pbar.refresh()  # Force immediate display update
        else:
            # Multi-threaded: use enhanced process_iter with progress callbacks
            worker = partial(
                ThreadRowUploader(client, collection_id).worker,
                is_merge=is_merge,
            )
            
            # Process with enhanced real-time updates
            for result in process_iter(worker, notion_rows, max_workers=max_threads):
                pbar.update(1)
                pbar.refresh()  # Force immediate display update
