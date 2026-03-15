import unicodedata
from typing import List

def smart_split_text(text: str, limit: int = 200) -> List[str]:
    """
    Splits text into chunks respecting constraints (newlines, sentences, spaces).
    Preserves the logic from the original bot but with type hints.
    """
    parts = []
    
    while text:
        if len(text) <= limit:
            parts.append(text)
            break
            
        split_index = -1
        
        # 1. Newlines
        newline_index = text.rfind('\n', 0, limit)
        if newline_index != -1:
            split_index = newline_index
        
        # 2. Sentences
        if split_index == -1:
            for char in ['. ', '! ', '? ']:
                idx = text.rfind(char, 0, limit)
                if idx != -1 and idx + 1 > split_index:
                    split_index = idx + 1
        
        # 3. Spaces
        if split_index == -1:
            space_index = text.rfind(' ', 0, limit)
            if space_index != -1:
                split_index = space_index
                
        # 4. Hard truncation
        if split_index == -1:
            split_index = limit
            
        chunk = text[:split_index].strip()
        if chunk:
            parts.append(chunk)
        
        text = text[split_index:].strip()
        
    return parts

def clean_twitter_text(text: str) -> str:
    """Removes unwanted characters or formatting."""
    return text.replace('"', '').replace("'", "").strip()


def sanitize_http_header_value(
    value: str,
    fallback: str = "Tarihte Bugun Botu"
) -> str:
    """Normalizes header values to ASCII because HTTP headers are ASCII-only."""
    normalized_value = unicodedata.normalize("NFKD", value)
    ascii_value = normalized_value.encode("ascii", "ignore").decode("ascii")
    compact_value = " ".join(ascii_value.split())
    if compact_value:
        return compact_value
    return fallback
