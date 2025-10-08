"""
CSV2Notion Neo - String Utilities

This module provides string processing utilities for data manipulation,
including string splitting functions used for parsing CSV data and
handling multi-value fields in Notion databases.
"""

from typing import List
from icecream import ic


def split_str(s: str, sep: str = ",") -> List[str]:

    if type(s) == list:
        return ["".join(item.split(",")) for item in s]

    return [v.strip() for v in s.split(sep) if v.strip()]
