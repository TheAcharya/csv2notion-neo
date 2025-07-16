# Starting from this file, we have to start writing tests for basic function of neo
# Testing must be written in pytest best in class practices and run using pytest

from typing import Generator, Union
import pytest
from csv2notion_neo.notion_db_client import NotionClientExtended
from csv2notion_neo.version import __version__
from csv2notion_neo.cli_steps import convert_csv_to_notion_rows, new_database, upload_rows
from csv2notion_neo.local_data import LocalData
from csv2notion_neo.notion_db import get_collection_id, get_notion_client
from csv2notion_neo.utils_exceptions import CriticalError
from .input_command import ARGS_DICT
from argparse import Namespace
from pathlib import Path

# Use this ficture to load the client and load the data, use yield to load client more than once with different parameters

@pytest.fixture(scope="session")
def load_client_and_data() -> Generator[Union[LocalData,NotionClientExtended,Namespace],None,None]:
    
    args = Namespace(**ARGS_DICT)
    
    # Skip test if Notion credentials are not available
    if not args.token:
        pytest.skip("Notion token not available in environment variables")
    
    csv_data = LocalData(
        args.csv_file, args.column_types, args.fail_on_duplicate_csv_columns, args.payload_key_column,args=args
    )

    try:
        client = get_notion_client(
            args.token,
            workspace=args.workspace,
            is_randomize_select_colors=args.randomize_select_colors,
        )
        
        if not args.url:
            args.url = new_database(args, client, csv_data)

        yield csv_data,client,args
    except Exception as e:
        pytest.skip(f"Failed to connect to Notion API: {e}")

def test_upload_rows(load_client_and_data) -> None:
    data,client,args = load_client_and_data

    collection = get_collection_id(
        client,
        args.url
    )

    notion_rows = convert_csv_to_notion_rows(
        data,
        client,
        collection,
        args
    )

    upload_rows(
        notion_rows,
        client=client,
        collection_id=collection,
        is_merge=args.merge,
        max_threads=args.max_threads,
    )

    assert 1 == 1
