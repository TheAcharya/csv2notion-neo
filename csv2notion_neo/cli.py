"""
CSV2Notion Neo - Command Line Interface

This module provides the main CLI interface for CSV2Notion Neo.
It handles argument parsing, data processing, and orchestrates the upload process
to Notion databases using the official Notion API.
"""

import logging
import os
import signal
import sys
from pathlib import Path
from typing import Any, Optional
from icecream import ic

from csv2notion_neo.version import __version__
from csv2notion_neo.cli_args import parse_args
from csv2notion_neo.cli_steps import (
    convert_csv_to_notion_rows,
    new_database,
    upload_rows,
    delete_all_database_entries,
)
from csv2notion_neo.local_data import LocalData
from csv2notion_neo.notion_db import get_collection_id, get_notion_client
from csv2notion_neo.utils_exceptions import CriticalError, NotionError

logger = logging.getLogger(__name__)


def cli(*argv: str) -> None:
    try:
        ic.enable()
        args = parse_args(argv)

        setup_logging(is_verbose=args.verbose, log_file=args.log)
        logger.info(f"CSV2Notion Neo version {__version__}")

        client = get_notion_client(
            args.token,
            workspace=args.workspace,
            is_randomize_select_colors=args.randomize_select_colors,
        )

        # Handle delete all database entries operation
        if hasattr(args, 'delete_all_database_entries') and args.delete_all_database_entries:
            if not args.url:
                raise CriticalError("Database URL is required for --delete-all-database-entries operation")
            
            collection_id = get_collection_id(client, args.url)
            
            # Check if a page URL was provided instead of a database URL
            if collection_id.startswith("PAGE:"):
                raise CriticalError(
                    "Page URL provided, but --delete-all-database-entries requires a database URL. "
                    "Please provide the URL of an existing Notion database, not a page."
                )
            
            deleted_count = delete_all_database_entries(client, collection_id)
            
            if deleted_count == 0:
                logger.info("Database is already empty - no entries to delete")
            else:
                logger.info(f"Successfully deleted {deleted_count} entries from database")
            return

        # Check if file is provided for normal operations
        if not args.csv_file:
            raise CriticalError("CSV or JSON file is required for upload operations")

        # Process file type and validation
        path = Path(args.csv_file).suffix

        if "json" in path:
            if not args.payload_key_column:
                raise CriticalError("Json file found, please enter the key column!")

        logger.info(f"Validating {path[1::]} & csv2notion_neo.notion DB schema")

        csv_data = LocalData(
            args.csv_file,
            args.column_types,
            args.fail_on_duplicate_csv_columns,
            args.payload_key_column,
            args=args,
        )

        if not csv_data:
            raise CriticalError(f"{path} file is empty")

        if not args.url:
            args.url = new_database(args, client, csv_data)

        collection_id = get_collection_id(client, args.url)
        
        # Check if we got a page ID (indicated by PAGE: prefix)
        if collection_id.startswith("PAGE:"):
            page_id = collection_id[5:]  # Remove "PAGE:" prefix
            logger.info(f"Creating database within page: {page_id}")
            
            # Create database within the page
            skip_columns = []
            if args.image_column and not args.image_column_keep:
                skip_columns.append(args.image_column)
            if args.icon_column and not args.icon_column_keep:
                skip_columns.append(args.icon_column)
            if args.image_caption_column and not args.image_caption_column_keep:
                skip_columns.append(args.image_caption_column)
            
            from csv2notion_neo.notion_db import create_database_in_page
            database_url, database_id = create_database_in_page(
                client,
                page_id=page_id,
                database_name=args.csv_file.stem,  # This works for both CSV and JSON files
                csv_data=csv_data,
                skip_columns=skip_columns
            )
            
            logger.info(f"Database created within page. Database URL: {database_url}")
            collection_id = database_id
            
            # Add a small delay to ensure the database is fully ready
            import time
            time.sleep(2.0)
            logger.info("Database initialization complete, proceeding with upload...")

        notion_rows = convert_csv_to_notion_rows(csv_data, client, collection_id, args)

        logger.info("Uploading {0}...".format(args.csv_file.name))

        upload_rows(
            notion_rows,
            client=client,
            collection_id=collection_id,
            is_merge=args.merge,
            max_threads=args.max_threads,
        )

        logger.info("Done!")

    except Exception as e:
        # Check if args was successfully parsed to avoid UnboundLocalError
        if 'args' in locals() and hasattr(args, 'verbose') and args.verbose:
            logger.error("Error during execution", exc_info=e)
        else:
            logger.error(e)
        # Re-raise so callers can handle errors programmatically
        # (main() already catches NotionError/CriticalError for CLI usage)
        raise


def setup_logging(is_verbose: bool = False, log_file: Optional[Path] = None) -> None:
    logging.basicConfig(format="%(levelname)s: %(message)s")

    logging.getLogger("csv2notion_neo").setLevel(
        logging.DEBUG if is_verbose else logging.INFO
    )

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)-8.8s] %(message)s")
        )
        logging.getLogger("csv2notion_neo").addHandler(file_handler)

    logging.getLogger("csv2notion_neo.notion").setLevel(logging.WARNING)


def abort(*_: Any) -> None:  # pragma: no cover
    print("\nAbort")  # noqa: WPS421
    os._exit(1)


def main() -> None:
    signal.signal(signal.SIGINT, abort)

    try:
        cli(*sys.argv[1:])
    except (NotionError, CriticalError) as e:
        logger.critical(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)
