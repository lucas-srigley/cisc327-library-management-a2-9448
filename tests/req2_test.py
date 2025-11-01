import pytest
from services.library_service import (
    get_all_books
)
from database import (
    reset_db
)

@pytest.fixture(scope="module", autouse=True)
def reset_database():
    """Reset database after all tests in this module run."""
    yield
    reset_db()

def test_get_all_books_valid_input():
    """Test getting all books with valid input."""
    valid_input = [
        ("The Great Gatsby", "F. Scott Fitzgerald", "9780743273565", 3),
        ("To Kill a Mockingbird", "Harper Lee", "9780061120084", 2),
        ("1984", "George Orwell", "9780451524935", 1)
    ]
    assert len(valid_input) == len(get_all_books())
    for title, author, isbn, total_copies in valid_input:
        valid = False
        for book in get_all_books():
            if (book["title"] == title and
                book["author"] == author and
                book["isbn"] == isbn and
                book["total_copies"] == total_copies):
                valid = True
        assert valid == True

def test_get_all_books_invalid_input():
    """Test getting all books with invalid input/length."""
    invalid_input = [
        ("zzz", "zzz", "1234567890124", 5)
    ]
    assert len(invalid_input) != len(get_all_books())
    for title, author, isbn, total_copies in invalid_input:
        valid = False
        for book in get_all_books():
            if (book["title"] == title and
                book["author"] == author and
                book["isbn"] == isbn and
                book["total_copies"] == total_copies):
                valid = True
        assert valid == False

def test_get_all_books_valid_copies_ranges():
    """Test valid available/total copies ranges."""
    for book in get_all_books():
        assert 0 <= book["available_copies"] <= book["total_copies"]
        
def test_get_all_books_valid_copies():
    """Test valid available/total copies for a given book."""
    for book in get_all_books():
        if book['title'] == 'The Great Gatsby':
            assert book['available_copies'] == 3
            assert book['total_copies'] == 3
