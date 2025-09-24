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
    worker = partial(
        ThreadRowUploader(client, collection_id).worker,
        is_merge=is_merge,
    )

    tdqm_iter = tqdm(
        iterable=process_iter(worker, notion_rows, max_workers=max_threads),
        total=len(notion_rows),
        leave=False,
    )

    # Consume iterator
    list(tdqm_iter)
