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
    yield
    reset_db()

import pytest
from library_service import (
    search_books_in_catalog
)

def test_search_books_partial_title():
    results = search_books_in_catalog("19", "title")
    assert len(results) == 1
    assert results[0]["title"] == "1984" 

def test_search_books_partial_author():
    results = search_books_in_catalog("geo", "author")
    assert len(results) == 1
    assert results[0]["author"] == "George Orwell" 
    
def test_search_books_partial_isbn():
    results = search_books_in_catalog("978045152493", "isbn")
    assert len(results) == 0
    
def test_search_books_exact_isbn():
    results = search_books_in_catalog("9780451524935", "isbn")
    assert len(results) == 1
    assert results[0]["isbn"] == "9780451524935"
