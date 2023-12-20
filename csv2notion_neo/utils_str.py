from typing import List


def split_str(s: str, sep: str = ",") -> List[str]:
    
    if type(s) == list:
        return ["".join(item.split(",")) for item in s]
    
    return [v.strip() for v in s.split(sep) if v.strip()]
