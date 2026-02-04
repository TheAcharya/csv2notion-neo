"""
Unit tests for NotionDB caching behavior, particularly error handling.

This test suite ensures that when database fetch fails (e.g., timeouts, 503 errors),
the cache is not populated with invalid data that could cause duplicate entries.
"""

import pytest
from unittest.mock import Mock, MagicMock
from csv2notion_neo.notion_db import NotionDB
from csv2notion_neo.utils_exceptions import NotionError


class TestNotionDBCacheBehavior:
    """Test caching behavior of NotionDB.rows property."""

    def test_rows_cache_not_set_on_fetch_failure(self):
        """
        CRITICAL BUG FIX TEST:
        When database fetch fails (timeout, 503, etc.), the rows cache should NOT
        be set to an empty dict. This would cause subsequent accesses to think the
        database is empty, leading to duplicate entries being created.
        
        This test reproduces the bug from the debug log where:
        - Initial fetch failed with "Request to Notion API has timed out"
        - Cache was set to {} despite the error
        - Upload continued and created duplicates
        """
        # Create a mock client that will fail on query
        mock_client = Mock()
        mock_client.query_database.side_effect = Exception("Request to Notion API has timed out")
        
        # Create NotionDB instance
        db = NotionDB(mock_client, "test-database-id")
        
        # Mock the columns property to avoid another API call
        db._cache_columns = {"Title": {"type": "title"}}
        
        # Accessing rows should raise NotionError, not return empty dict
        with pytest.raises(NotionError, match="Cannot query database"):
            _ = db.rows
        
        # CRITICAL: Cache should remain None, not be set to {}
        assert db._cache_rows is None, (
            "Cache was incorrectly set despite fetch failure! "
            "This bug causes duplicate entries when upload continues."
        )

    def test_rows_cache_set_on_successful_fetch(self):
        """
        Verify that cache IS set when fetch succeeds.
        """
        # Create a mock client that returns valid data
        mock_client = Mock()
        mock_client.query_database.return_value = {
            "results": [
                {
                    "id": "page-1",
                    "properties": {
                        "Title": {
                            "title": [{"text": {"content": "Test Entry"}}]
                        }
                    }
                }
            ],
            "has_more": False,
            "next_cursor": None
        }
        
        # Create NotionDB instance
        db = NotionDB(mock_client, "test-database-id")
        db._cache_columns = {"Title": {"type": "title"}}
        
        # Access rows
        rows = db.rows
        
        # Cache should be populated
        assert db._cache_rows is not None
        assert "Test Entry" in rows
        assert rows["Test Entry"]["id"] == "page-1"

    def test_rows_cache_prevents_duplicate_fetch(self):
        """
        Verify that once cache is set, subsequent accesses don't re-query.
        """
        mock_client = Mock()
        mock_client.query_database.return_value = {
            "results": [],
            "has_more": False,
            "next_cursor": None
        }
        
        db = NotionDB(mock_client, "test-database-id")
        db._cache_columns = {"Title": {"type": "title"}}
        
        # First access
        _ = db.rows
        assert mock_client.query_database.call_count == 1
        
        # Second access should use cache
        _ = db.rows
        assert mock_client.query_database.call_count == 1  # Still 1, not 2

    def test_invalidate_cache_allows_refetch(self):
        """
        Verify that invalidate_cache() clears the cache and allows re-fetch.
        """
        mock_client = Mock()
        mock_client.query_database.return_value = {
            "results": [],
            "has_more": False,
            "next_cursor": None
        }
        
        db = NotionDB(mock_client, "test-database-id")
        db._cache_columns = {"Title": {"type": "title"}}
        
        # First access
        _ = db.rows
        assert mock_client.query_database.call_count == 1
        
        # Invalidate cache
        db.invalidate_cache()
        
        # Second access should re-fetch
        _ = db.rows
        assert mock_client.query_database.call_count == 2

    def test_partial_fetch_failure_doesnt_cache(self):
        """
        If fetch fails midway through pagination, cache should not be set.
        """
        mock_client = Mock()
        
        # First page succeeds, second page fails
        call_count = 0
        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return {
                    "results": [
                        {
                            "id": "page-1",
                            "properties": {
                                "Title": {"title": [{"text": {"content": "Entry 1"}}]}
                            }
                        }
                    ],
                    "has_more": True,
                    "next_cursor": "cursor-1"
                }
            else:
                raise Exception("Request to Notion API failed with status: 503")
        
        mock_client.query_database.side_effect = side_effect
        
        db = NotionDB(mock_client, "test-database-id")
        db._cache_columns = {"Title": {"type": "title"}}
        
        # Accessing rows should fail
        with pytest.raises(NotionError):
            _ = db.rows
        
        # Cache should NOT be set to partial data
        assert db._cache_rows is None
