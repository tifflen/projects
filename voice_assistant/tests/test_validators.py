"""Unit tests for validators module."""

import pytest
from validators import (
    validate_audio_file,
    validate_text_input,
    validate_language_code,
    sanitize_json_response,
)

def test_validate_text_input_valid():
    """Test validation of valid text input."""
    is_valid, error = validate_text_input("Hello, world!")
    assert is_valid is True
    assert error == ""

def test_validate_text_input_empty():
    """Test validation of empty text."""
    is_valid, error = validate_text_input("")
    assert is_valid is False
    assert "empty" in error.lower()

def test_validate_text_input_too_long():
    """Test validation of text exceeding max length."""
    long_text = "a" * 2000
    is_valid, error = validate_text_input(long_text, max_length=1000)
    assert is_valid is False
    assert "exceeds" in error.lower()

def test_validate_text_input_whitespace_only():
    """Test validation of whitespace-only text."""
    is_valid, error = validate_text_input("   \n\t   ")
    assert is_valid is False
    assert "whitespace" in error.lower()

def test_validate_language_code_valid():
    """Test validation of valid language codes."""
    for code in ["en-US", "es-ES", "fr-FR", "de-DE"]:
        is_valid, error = validate_language_code(code)
        assert is_valid is True, f"Failed for {code}"

def test_validate_language_code_invalid():
    """Test validation of invalid language codes."""
    invalid_codes = ["123-45", "en", "", "en-US-invalid"]
    for code in invalid_codes:
        is_valid, error = validate_language_code(code)
        assert is_valid is False, f"Should fail for {code}"

def test_sanitize_json_response():
    """Test JSON response sanitization."""
    data = {
        "text": "Hello\x00World",
        "nested": {
            "field": "value\x01test"
        },
        "list": ["item1", "item\x02two"],
        "number": 42
    }
    
    sanitized = sanitize_json_response(data)
    
    # Null bytes and control characters should be removed
    assert "\x00" not in sanitized["text"]
    assert "\x01" not in sanitized["nested"]["field"]
    assert "\x02" not in sanitized["list"][1]
    
    # Regular content should be preserved
    assert "Hello" in sanitized["text"]
    assert "World" in sanitized["text"]
    assert sanitized["number"] == 42