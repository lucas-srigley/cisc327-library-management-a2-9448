import pytest
from services.library_service import (
    return_book_by_patron, get_book_by_isbn, borrow_book_by_patron
)
from database import (
    reset_db
)

@pytest.fixture(scope="module", autouse=True)
def reset_database():
    """Reset database after all tests in this module run."""
    yield
    reset_db()

def test_return_book_valid_input():
    """Test returning a book with valid input."""
    borrow_book_by_patron("123456", get_book_by_isbn("9780451524935")["id"])
    success, message = return_book_by_patron("123456", get_book_by_isbn("9780451524935")["id"])
    assert success == True
    assert "Successfully returned" in message

def test_return_book_invalid_patron_id_empty():
    """Test returning a book with empty patron id."""
    success, message = return_book_by_patron("", get_book_by_isbn("9780451524935")["id"])
    assert success == False
    assert "Invalid patron ID. Must be exactly 6 digits." in message

def test_return_book_invalid_patron_id_too_long():
    """Test returning a book with patron id too long."""
    success, message = return_book_by_patron("1234567", get_book_by_isbn("9780451524935")["id"])
    assert success == False
    assert "Invalid patron ID. Must be exactly 6 digits." in message

def test_return_book_invalid_patron_id_not_an_integer():
    """Test returning a book with patron id not an integer."""
    success, message = return_book_by_patron("a123456", get_book_by_isbn("9780451524935")["id"])
    assert success == False
    assert "Invalid patron ID. Must be exactly 6 digits." in message

def test_return_book_invalid_book_id():
    """Test returning a book with invalid book id."""
    success, message = return_book_by_patron("123456", 123456)
    assert success == False
    assert "Book not found." in message