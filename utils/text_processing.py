import re
from typing import Optional


def extract_rank(query: str) -> Optional[int]:
    patterns = [
        r'rank\s+(?:is\s+)?(\d+)',
        r'got\s+(\d+)\s*rank',
        r'scored\s+(\d+)',
        r'(\d+)\s+rank',
        r'viteee\s+rank\s+(\d+)',
        r'my\s+rank\s+is\s+(\d+)',
        r'rank\s*:\s*(\d+)',
        r'(\d{4,6})',
    ]
    
    query_lower = query.lower()
    
    for pattern in patterns:
        match = re.search(pattern, query_lower)
        if match:
            rank = int(match.group(1))
            if 1 <= rank <= 200000:
                return rank
    
    return None
