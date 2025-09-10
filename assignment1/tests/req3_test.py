import pytest
from library_service import (
    borrow_book_by_patron, get_book_by_isbn
)
from database import (
    reset_db
)

@pytest.fixture(scope="module", autouse=True)
def reset_database():
    """Reset database after all tests in this module run."""
    yield
    reset_db()

def test_borrow_book_valid_input():
    """Test borrowing a book with valid input."""
    success, message = borrow_book_by_patron("123456", get_book_by_isbn("9780451524935")["id"])
    assert success == True
    assert "successfully borrowed" in message.lower()

def test_borrow_book_valid_updated_availability():
    """Test valid available/total copies for a given book after being borrowed."""
    book = get_book_by_isbn("9780451524935")
    assert book["available_copies"] == 0
    assert book["total_copies"] == 1

def test_borrow_book_invalid_patron_id_empty():
    """Test borrowing a book with empty patron id."""
    success, message = borrow_book_by_patron("", get_book_by_isbn("9780451524935")["id"])
    assert success == False
    assert "Invalid patron ID. Must be exactly 6 digits." in message

def test_borrow_book_invalid_patron_id_too_long():
    """Test borrowing a book with patron id too long."""
    success, message = borrow_book_by_patron("1234567", get_book_by_isbn("9780451524935")["id"])
    assert success == False
    assert "Invalid patron ID. Must be exactly 6 digits." in message

def test_borrow_book_invalid_patron_id_not_an_integer():
    """Test borrowing a book with patron id not an integer."""
    success, message = borrow_book_by_patron("a123456", get_book_by_isbn("9780451524935")["id"])
    assert success == False
    assert "Invalid patron ID. Must be exactly 6 digits." in message

def test_borrow_book_invalid_book_not_found():
    """Test borrowing a book with invalid book id."""
    success, message = borrow_book_by_patron("123456", 12345)
    assert success == False
    assert "Book not found." in message

def test_borrow_book_invalid_book_unavailable():
    """Test borrowing a book with unavailable book."""
    success, message = borrow_book_by_patron("123456", get_book_by_isbn("9780451524935")["id"])
    assert success == False
    assert "This book is currently not available." in message

def test_borrow_book_invalid_borrow_limit_exceeded():
    """Test borrowing a book with valid input."""
    success, message = borrow_book_by_patron("123456", get_book_by_isbn("9780743273565")["id"])
    assert success == True
    assert "successfully borrowed" in message.lower()
    success, message = borrow_book_by_patron("123456", get_book_by_isbn("9780743273565")["id"])
    assert success == True
    assert "successfully borrowed" in message.lower()
    success, message = borrow_book_by_patron("123456", get_book_by_isbn("9780743273565")["id"])
    assert success == True
    assert "successfully borrowed" in message.lower()
    success, message = borrow_book_by_patron("123456", get_book_by_isbn("9780061120084")["id"])
    assert success == True
    assert "successfully borrowed" in message.lower()
    success, message = borrow_book_by_patron("123456", get_book_by_isbn("9780061120084")["id"])
    assert success == False
    assert "You have reached the maximum borrowing limit of 5 books." in message