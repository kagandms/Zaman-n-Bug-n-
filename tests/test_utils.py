import pytest
from src.utils.text_utils import smart_split_text, clean_twitter_text

def test_smart_split_text_basic():
    text = "Short text."
    parts = smart_split_text(text, limit=50)
    assert len(parts) == 1
    assert parts[0] == "Short text."

def test_smart_split_text_long():
    text = "A" * 60
    parts = smart_split_text(text, limit=50)
    assert len(parts) == 2
    assert parts[0] == "A" * 50
    assert parts[1] == "A" * 10

def test_clean_twitter_text():
    text = "'Hello' \"World\""
    cleaned = clean_twitter_text(text)
    assert cleaned == "Hello World"
