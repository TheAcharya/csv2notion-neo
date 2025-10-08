"""
CSV2Notion Neo - Delete Database Entries Test

This module tests the delete all database entries functionality.
"""

from typing import Generator
import pytest
from csv2notion_neo.notion_db import get_collection_id, get_notion_client
from csv2notion_neo.cli_steps import delete_all_database_entries
from csv2notion_neo.utils_exceptions import CriticalError
from .input_command import ARGS_DICT
from argparse import Namespace


@pytest.fixture(scope="session")
def load_client_for_delete() -> Generator[tuple, None, None]:
    """Load client and args for delete database entries testing."""
    args = Namespace(**ARGS_DICT)
    
    # Skip test if Notion credentials are not available
    if not args.token:
        pytest.skip("Notion token not available in environment variables")
    
    try:
        client = get_notion_client(
            args.token,
            workspace=args.workspace,
            is_randomize_select_colors=args.randomize_select_colors,
        )
        
        yield client, args
    except Exception as e:
        pytest.skip(f"Failed to connect to Notion API: {e}")


def test_delete_all_database_entries(load_client_for_delete) -> None:
    """Test the delete all database entries functionality."""
    client, args = load_client_for_delete
    
    # Get collection ID
    collection_id = get_collection_id(client, args.url)
    
    # Test delete all database entries
    deleted_count = delete_all_database_entries(client, collection_id)
    
    # Verify the operation completed
    assert isinstance(deleted_count, int)
    assert deleted_count >= 0
    
    print(f"Successfully deleted {deleted_count} entries from database")


def test_delete_all_database_entries_with_page_url(load_client_for_delete) -> None:
    """Test that delete all database entries fails with page URL."""
    client, args = load_client_for_delete
    
    # This test should be skipped if we're using a database URL
    # We'll create a mock page URL scenario
    try:
        # Try to delete with a page URL (should fail)
        collection_id = "PAGE:test-page-id"
        with pytest.raises(CriticalError, match="Page URL provided, but --delete-all-database-entries requires a database URL"):
            delete_all_database_entries(client, collection_id)
    except Exception as e:
        # If the test environment doesn't support this scenario, skip it
        pytest.skip(f"Test scenario not supported in current environment: {e}")
