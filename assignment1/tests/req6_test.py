import pytest
from library_service import (
    search_books_in_catalog
)
from database import (
    reset_db
)

@pytest.fixture(autouse=True)
def reset_database():
    """Reset database after all tests in this module run."""
    reset_db()

def test_search_books_valid_input():
    """Test searching for books with valid input."""
    results = search_books_in_catalog("19", "title")
    assert results == []

def test_search_books_invalid_empty_term():
    """Test searching for books with empty search term."""
    success, message = search_books_in_catalog("", "title")
    assert success == False
    assert "Search term not found." in message 

def test_search_books_invalid_empty_type():
    """Test searching for books with empty search type."""
    success, message = search_books_in_catalog("1984", "")
    assert success == False
    assert "Search type not found." in message 
    
def test_search_books_invalid_type():
    """Test searching for books with invalid search type."""
    success, message = search_books_in_catalog("9780451524935", "isbns")
    assert success == False
    assert "Invalid search type." in message 