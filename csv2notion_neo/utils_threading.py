"""
CSV2Notion Neo - Threading Utilities

This module provides threading utilities for concurrent operations in CSV2Notion Neo.
It manages thread pools, concurrent uploads, and thread-safe operations to optimize
performance when processing large datasets.
"""

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Dict, Iterable, Iterator, Optional

from csv2notion_neo.notion_db import NotionDB
from csv2notion_neo.notion_client import NotionClient
from csv2notion_neo.notion_db_client import NotionClientExtended
from csv2notion_neo.notion_uploader import NotionRowUploader
from icecream import ic


class ThreadRowUploader(object):
    def __init__(self, client: NotionClient, collection_id: str) -> None:
        self.thread_data = threading.local()
        self.client = client
        self.collection_id = collection_id
        
        # Shared cache for merge operations to prevent race conditions
        self._shared_cache_lock = threading.Lock()
        self._shared_cache = None

    def worker(self, *args: Any, **kwargs: Any) -> None:
        try:
            notion_uploader = self.thread_data.uploader
        except AttributeError:
            # Create a new extended client for this thread
            client = NotionClientExtended(
                integration_token=self.client.integration_token,
                workspace=self.client.workspace,
                options=self.client.options
            )
            notion_db = NotionDB(client, self.collection_id)

            notion_uploader = NotionRowUploader(notion_db)
            self.thread_data.uploader = notion_uploader

        # Execute the upload with progress tracking
        notion_uploader.upload_row(*args, **kwargs)
        
        # Add a small yield point to allow other threads to update progress
        import time
        time.sleep(0.001)  # 1ms to allow progress bar updates
    
    def get_shared_cache(self) -> Optional[Dict[str, Any]]:
        """Get shared cache for merge operations."""
        with self._shared_cache_lock:
            return self._shared_cache
    
    def update_shared_cache(self, key: str, value: Any) -> None:
        """Update shared cache for merge operations."""
        with self._shared_cache_lock:
            if self._shared_cache is None:
                self._shared_cache = {}
            self._shared_cache[key] = value
    
    def invalidate_shared_cache(self) -> None:
        """Invalidate shared cache."""
        with self._shared_cache_lock:
            self._shared_cache = None


def process_iter(
    worker: Callable[[Any], None], tasks: Iterable[Any], max_workers: int
) -> Iterator[None]:
    if max_workers == 1:
        # Single-threaded: yield immediately after each task
        for task in tasks:
            worker(task)
            yield None  # Yield immediately for progress bar update
    else:
        # Multi-threaded: enhanced real-time processing
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks and create a mapping of future to task
            future_to_task = {executor.submit(worker, task): task for task in tasks}
            
            # Process completed futures as they finish with enhanced real-time updates
            completed_count = 0
            total_tasks = len(future_to_task)
            
            for future in as_completed(future_to_task):
                try:
                    # Get the result (this will raise an exception if the task failed)
                    result = future.result()
                    completed_count += 1
                    
                    # Yield immediately to update progress bar in real-time
                    yield result
                    
                    # Optional: Add a small delay to ensure progress bar updates are visible
                    # This helps with very fast operations where updates might be missed
                    if completed_count % 10 == 0:  # Every 10 completions
                        import time
                        time.sleep(0.001)  # 1ms delay to ensure UI updates
                        
                except Exception as e:
                    # Log the error but continue processing other tasks
                    ic(f"Task failed: {e}")
                    completed_count += 1
                    # Still yield to maintain progress bar accuracy
                    yield None
