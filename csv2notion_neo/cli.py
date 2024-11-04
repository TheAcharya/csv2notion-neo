import logging
import os
import signal
import sys
from pathlib import Path
from typing import Any, Optional
from icecream import ic

from csv2notion_neo.version import __version__
from csv2notion_neo.cli_args import parse_args
from csv2notion_neo.cli_steps import convert_csv_to_notion_rows, new_database, upload_rows
from csv2notion_neo.local_data import LocalData
from csv2notion_neo.notion_db import get_collection_id, get_notion_client
from csv2notion_neo.utils_exceptions import CriticalError, NotionError

logger = logging.getLogger(__name__)


def cli(*argv: str) -> None:
    try:
        ic.disable()
        args = parse_args(argv)
            
        setup_logging(is_verbose=args.verbose, log_file=args.log)
        logger.info(f"CSV2Notion Neo version {__version__}")

        path = Path(args.csv_file).suffix

        if "json" in path:
            if not args.payload_key_column:
                raise CriticalError("Json file found, please enter the key column!")
            
        logger.info(f"Validating {path[1::]} & csv2notion_neo.notion DB schema")

        csv_data = LocalData(
            args.csv_file, args.column_types, args.fail_on_duplicate_csv_columns, args.payload_key_column,args=args
        )

        if not csv_data:
            raise CriticalError(f"{path} file is empty")

        client = get_notion_client(
            args.token,
            workspace=args.workspace,
            is_randomize_select_colors=args.randomize_select_colors,
        )

        if not args.url:
            args.url = new_database(args, client, csv_data)
        
        collection_id = get_collection_id(client, args.url)

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
        if args.verbose:
            logger.error('Error at %s', 'division', exc_info=e)
        else:
            logger.error(e)


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
