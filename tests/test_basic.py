# Starting from this file, we have to start writing tests for basic function of neo
# Testing must be written in pytest best in class practices and run using pytest

from typing import Generator, Union
import pytest
from csv2notion_neo.notion_db_client import NotionClientExtended
from csv2notion_neo.version import __version__
from csv2notion_neo.cli_args import parse_args
from csv2notion_neo.cli_steps import convert_csv_to_notion_rows, new_database, upload_rows
from csv2notion_neo.local_data import LocalData
from csv2notion_neo.notion_db import get_collection_id, get_notion_client
from csv2notion_neo.utils_exceptions import CriticalError, NotionError
# Use this ficture to load the client and load the data, use yield to load client more than once with different parameters
@pytest.fixture(scope="session")
def load_client_and_data() -> Generator[Union[LocalData,NotionClientExtended],None,None]:
    print("setting up the notion client and loading the data for test!")
    yield 1,2
    print("client and data loaded!")

def test_basic(load_client_and_data) -> None:
    client, data = load_client_and_data
    print(client,data)
    assert 1 == 1
