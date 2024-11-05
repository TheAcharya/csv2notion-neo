import math
import re
from typing import List
from icecream import ic

def guess_type_by_values(values_str: List[str]) -> str:

    if type(values_str[0]) == list:
        unique_values = set(map(tuple, values_str))
    else:   
        unique_values = set(filter(None, values_str))

    match_map = {
        "text": is_empty,
        "checkbox": is_checkbox,
        "number": is_number,
        "url": is_url,
        "email": is_email,
        "multi_select": is_multi
    }

    matches = (
        value_type
        for value_type, match_func in match_map.items()
        if all(map(match_func, unique_values))
    )
           
    return next(matches, "text")


def is_number(s: str) -> bool:
    try:
        return not math.isnan(float(s))
    except:
        return False

def is_multi(s) -> bool:
    
    try:
        if type(s) == tuple:
            return True
    except:
        return None
    
def is_url(s: str) -> bool:

    try:
        return re.match("^https?://", s) is not None
    except:
        return None


def is_email(s: str) -> bool:
    try:
        return re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", s) is not None
    except:
        return None


def is_checkbox(s: str) -> bool:
    try:
        return s in {"true", "false"}
    except:
        return None


def is_empty(s: str) -> bool:

    try:
        return not s.strip()
    except:
        return None
