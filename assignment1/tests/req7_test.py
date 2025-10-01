import pytest
from datetime import datetime, timedelta
from library_service import (
    get_patron_status_report, borrow_book_by_patron, get_book_by_isbn
)
from database import (
    reset_db, insert_book, insert_borrow_record
)

@pytest.fixture(scope="module", autouse=True)
def reset_database():
    """Reset database after all tests in this module run."""
    yield
    reset_db()

def test_get_patron_status_report_valid_input():
    """Test getting patron status report with valid input."""
    result = get_patron_status_report("123456")
    assert result['success'] == True
    assert result['patron_id'] == "123456"
    assert 'currently_borrowed' in result
    assert 'num_books_borrowed' in result
    assert 'total_late_fees' in result

def test_get_patron_status_report_invalid_patron_id_empty():
    """Test getting patron status report with empty patron id."""
    result = get_patron_status_report("")
    assert result['success'] == False
    assert "Invalid patron ID. Must be exactly 6 digits." in result['message']

def test_get_patron_status_report_invalid_patron_id_too_long():
    """Test getting patron status report with patron id too long."""
    result = get_patron_status_report("1234567")
    assert result['success'] == False
    assert "Invalid patron ID. Must be exactly 6 digits." in result['message']

def test_get_patron_status_report_invalid_patron_id_not_an_integer():
    """Test getting patron status report with patron id not an integer."""
    result = get_patron_status_report("a12345")
    assert result['success'] == False
    assert "Invalid patron ID. Must be exactly 6 digits." in result['message']

def test_get_patron_status_report_with_borrowed_books():
    """Test getting patron status report with borrowed books."""
    book_id = get_book_by_isbn("9780743273565")["id"]
    borrow_book_by_patron("234567", book_id)
    
    result = get_patron_status_report("234567")
    assert result['success'] == True
    assert result['num_books_borrowed'] == 1
    assert len(result['currently_borrowed']) == 1
    assert result['borrowing_limit_remaining'] == 4

def test_get_patron_status_report_with_overdue_book():
    """Test patron status report with overdue book and late fees."""
    insert_book("Overdue Test Book", "Test Author", "9780743273566", total_copies=1, available_copies=0)
    book_id = get_book_by_isbn("9780743273566")["id"]
    
    borrow_date = datetime.now() - timedelta(days=20)
    due_date = borrow_date + timedelta(days=14)
    insert_borrow_record("345678", book_id, borrow_date, due_date)
    
    result = get_patron_status_report("345678")
    assert result['success'] == True
    assert result['total_late_fees'] > 0
    assert result['currently_borrowed'][0]['is_overdue'] == True

def test_get_patron_status_report_no_books():
    """Test patron status report with no borrowed books."""
    result = get_patron_status_report("456789")
    assert result['success'] == True
    assert result['num_books_borrowed'] == 0
    assert result['total_late_fees'] == 0.00
    assert result['borrowing_limit_remaining'] == 5