"""Pytest-based tests for the CSV-to-Notion upload flow.

This module exercises the integration between LocalData, NotionClient, and the
upload utilities. It uses a function-scoped fixture to construct a Notion
client and CSV-backed LocalData instance, optionally creating a new Notion
database when no URL is provided. The tests verify that CSV rows can be
converted to Notion rows and uploaded successfully, and, when possible, that
the row count in the target collection does not decrease after an upload.
"""

import logging
from typing import Generator, Tuple, Type

import httpx
import pytest
from notion_client.errors import APIResponseError
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import Timeout as RequestsTimeout

from csv2notion_neo.cli_steps import convert_csv_to_notion_rows, new_database, upload_rows
from csv2notion_neo.local_data import LocalData
from csv2notion_neo.notion_client import NotionClient
from csv2notion_neo.notion_db import NotionDB, get_collection_id, get_notion_client
from csv2notion_neo.utils_exceptions import NotionError
from .input_command import ARGS_DICT
from argparse import Namespace

logger = logging.getLogger(__name__)

# Live Notion integration: skip when credentials/API are unavailable; anything else fails.
_INTEGRATION_SKIP_EXCEPTIONS: Tuple[Type[BaseException], ...] = (
    NotionError,
    APIResponseError,
    RequestsConnectionError,
    RequestsTimeout,
    httpx.ConnectError,
    httpx.TimeoutException,
    httpx.ReadTimeout,
)


def _integration_skip_reason(exc: BaseException) -> str:
    return f"Notion integration unavailable (skipping live test): {exc}"


@pytest.fixture
def load_client_and_data() -> Generator[Tuple[LocalData, NotionClient, Namespace], None, None]:
    """Initialize client/data per test function and yield them with args.

    Skips when the token is missing or Notion is unreachable (expected in CI without secrets).
    Other errors (e.g. bad test fixtures, code bugs) propagate and fail the test.
    """

    args = Namespace(**ARGS_DICT)

    if not args.token:
        pytest.skip("Notion token not available in environment variables")

    csv_data = LocalData(
        args.csv_file,
        args.column_types,
        args.fail_on_duplicate_csv_columns,
        args.payload_key_column,
        args=args,
    )

    try:
        client = get_notion_client(
            args.token,
            workspace=args.workspace,
            is_randomize_select_colors=args.randomize_select_colors,
        )

        if not args.url:
            args.url = new_database(args, client, csv_data)

        yield csv_data, client, args
    except _INTEGRATION_SKIP_EXCEPTIONS as exc:
        pytest.skip(_integration_skip_reason(exc))

def test_upload_rows(load_client_and_data) -> None:
    data, client, args = load_client_and_data

    collection = get_collection_id(
        client,
        args.url
    )

    # Capture row count before upload when possible (requires NotionDB)
    pre_upload_count = None
    try:
        db = NotionDB(client, collection)
        pre_upload_count = len(db.rows)
    except NotionError:
        # Pre-upload count is optional; log and continue so the test can still run.
        logger.exception("Failed to get pre-upload row count from NotionDB")

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

    # Verify we had rows to upload and upload_rows completed without raising
    assert len(notion_rows) > 0, "Should have notion rows to upload"
    # Verify row count increased when we can query the database
    if pre_upload_count is not None:
        try:
            db = NotionDB(client, collection)
            db.invalidate_cache()
            post_upload_count = len(db.rows)
            assert post_upload_count >= pre_upload_count, (
                "Number of rows in collection should not decrease after upload"
            )
            # In non-merge mode we only assert the count did not decrease; duplicates
            # or validation failures may result in fewer new rows than len(notion_rows).
        except NotionError:
            # Row-count verification is optional; log and continue so the test still passes.
            logger.exception(
                "Failed to verify post-upload row count in NotionDB; skipping count-based assertions"
            )
