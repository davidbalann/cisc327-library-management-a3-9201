import pytest
import sys
import os
import random
import string

# Allow importing library_service & database from parent dir
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from library_service import add_book_to_catalog
from database import get_book_by_isbn, insert_book  # used for setup/verification

# --- helpers ---------------------------------------------------------------

def unique_isbn():
    """Generate a 13-digit numeric ISBN not present in DB (best-effort)."""
    # Try a few times to avoid rare collisions
    for _ in range(10):
        isbn = ''.join(random.choice(string.digits) for _ in range(13))
        if get_book_by_isbn(isbn) is None:
            return isbn
    # Fallback: still return a 13-digit string; last resort may collide
    return ''.join(random.choice(string.digits) for _ in range(13))

# ------------------------
# R1: six integration tests
# ------------------------

def test_add_book_valid_input():
    """Happy path: valid fields create a real DB row."""
    isbn = unique_isbn()
    success, message = add_book_to_catalog("Test Book", "Test Author", isbn, 5)
    assert success is True
    assert "successfully added" in message.lower()

    row = get_book_by_isbn(isbn)
    assert row is not None


def test_add_book_missing_title():
    """Title is required."""
    isbn = unique_isbn()
    success, message = add_book_to_catalog("", "Author", isbn, 1)
    assert success is False
    assert "title is required" in message.lower()

def test_add_book_author_required():
    """Author is required."""
    isbn = unique_isbn()
    success, message = add_book_to_catalog("Some Title", "   ", isbn, 1)
    assert success is False
    assert "author is required" in message.lower()

def test_add_book_invalid_isbn_length():
    """ISBN must be exactly 13 digits (implementation checks length)."""
    success, message = add_book_to_catalog("T", "A", "123456789", 1)
    assert success is False
    assert "exactly 13" in message

def test_add_book_invalid_total_copies_nonpositive():
    """Total copies must be a positive integer (zero should fail)."""
    isbn = unique_isbn()
    success, message = add_book_to_catalog("T", "A", isbn, -1)
    assert success is False
    assert "positive integer" in message.lower()

def test_add_book_duplicate_isbn():
    """Duplicate ISBN must be rejected. Set up real row first, then call service."""
    isbn = unique_isbn()
    ok = insert_book("Seed Title", "Seed Author", isbn, 1, 1)
    assert ok is True

    success, message = add_book_to_catalog("New Title", "New Author", isbn, 2)
    assert success is False
    assert "already exists" in message.lower()

def test_add_book_title_too_long():
    """Title > 200 chars should be rejected."""
    isbn = unique_isbn()
    long_title = "A" * 201  # 201 chars
    success, message = add_book_to_catalog(long_title, "Author", isbn, 1)
    assert success is False
    assert "less than 200" in message.lower()


def test_add_book_author_too_long():
    """Author > 100 chars should be rejected."""
    isbn = unique_isbn()
    long_author = "B" * 101  # 101 chars
    success, message = add_book_to_catalog("Some Title", long_author, isbn, 1)
    assert success is False
    assert "less than 100" in message.lower()

