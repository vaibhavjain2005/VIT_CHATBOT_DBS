import re
from datetime import datetime
from typing import Optional, Tuple


def extract_rank_and_year(query: str) -> Tuple[Optional[int], Optional[int]]:
    """Extract both rank and year from the query if present."""
    rank = extract_rank(query)
    year = extract_year(query)
    return rank, year


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

def extract_year(query: str) -> Optional[int]:
    """Extract year mention from the query."""
    patterns = [
        r'(?:in|for|year)\s+(?:20)?(\d{2})',  # matches "in 23", "for 2023"
        r'(?:20)?(\d{2})\s+batch',  # matches "23 batch", "2023 batch"
        r'batch\s+(?:20)?(\d{2})',  # matches "batch 23", "batch 2023"
        r'(?:20)?(\d{2})\s+admission',  # matches "23 admission", "2023 admission"
        r'viteee\s+(?:20)?(\d{2})',  # matches "viteee 23", "viteee 2023"
    ]
    
    current_year = datetime.now().year
    min_valid_year = current_year - 5  # Allow checking past 5 years
    max_valid_year = current_year + 1  # Allow checking next year
    
    query_lower = query.lower().strip()
    
    for pattern in patterns:
        match = re.search(pattern, query_lower)
        if match:
            year_str = match.group(1)
            if len(year_str) == 2:
                # Convert 2-digit year to 4-digit
                year = 2000 + int(year_str)
            else:
                year = int(year_str)
            
            # Validate year range
            if min_valid_year <= year <= max_valid_year:
                return year
    
    return None


def normalize_year(year: Optional[int]) -> Optional[int]:
    """Normalize and validate a year value."""
    if year is None:
        return None
        
    current_year = datetime.now().year
    
    # If it's a 2-digit year, convert to 4-digit
    if year < 100:
        year = 2000 + year
    
    # Validate year is within reasonable range
    if current_year - 5 <= year <= current_year + 1:
        return year
    
    return None
