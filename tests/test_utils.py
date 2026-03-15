import pytest
from src.utils.text_utils import (
    clean_twitter_text,
    sanitize_http_header_value,
    smart_split_text,
)

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


def test_sanitize_http_header_value_transliterates_non_ascii():
    text = "Tarihte Bugün Botu (Elite Edition)"

    cleaned = sanitize_http_header_value(text)

    assert cleaned == "Tarihte Bugun Botu (Elite Edition)"


def test_sanitize_http_header_value_uses_fallback_when_empty():
    cleaned = sanitize_http_header_value("🕊️", fallback="History Bot")

    assert cleaned == "History Bot"
