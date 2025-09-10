from datetime import datetime, timedelta
import pytest
from library_service import (
    calculate_late_fee_for_book, get_book_by_isbn
)
from database import (
    reset_db
)

@pytest.fixture(autouse=True)
def reset_database():
    """Reset database after all tests in this module run."""
    reset_db()

def test_calculate_late_fee_valid_input():
    """Test calculating late fee with valid input."""
    result = calculate_late_fee_for_book("123456", get_book_by_isbn("9780451524935")["id"])
    assert result["fee_amount"] == 0.00
    assert result["days_overdue"] == 0
    assert result["status"] == "Late fee calculation not implemented"

def test_calculate_late_fee_invalid_patron_id_empty():
    """Test calculating late fee with empty patron id."""
    success, message = calculate_late_fee_for_book("", get_book_by_isbn("9780451524935")["id"])
    assert success == False
    assert "Invalid patron ID. Must be exactly 6 digits." in message

def test_calculate_late_fee_invalid_patron_id_too_long():
    """Test calculating late fee with patron id too long."""
    success, message = calculate_late_fee_for_book("1234567", get_book_by_isbn("9780451524935")["id"])
    assert success == False
    assert "Invalid patron ID. Must be exactly 6 digits." in message

def test_calculate_late_fee_invalid_patron_id_not_an_integer():
    """Test calculating late fee with patron id not an integer."""
    success, message = calculate_late_fee_for_book("a123456", get_book_by_isbn("9780451524935")["id"])
    assert success == False
    assert "Invalid patron ID. Must be exactly 6 digits." in message

def test_calculate_late_fee_invalid_book_id():
    """Test calculating late fee with invalid book id."""
    success, message = calculate_late_fee_for_book("123456", 123456)
    assert success == False
    assert "Book not found." in message