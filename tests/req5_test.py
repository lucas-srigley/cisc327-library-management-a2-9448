from datetime import datetime, timedelta
import pytest
from services.library_service import (
    calculate_late_fee_for_book, get_book_by_isbn, insert_borrow_record, insert_book
)
from database import (
    reset_db
)

@pytest.fixture(autouse=True)
def reset_database():
    """Reset database after all tests in this module run."""
    yield
    reset_db()

def test_calculate_late_fee_for_book_not_overdue():
    """Test calculating late fee for book not overdue."""
    insert_book("Test Book", "Test Author", "1234567890124", total_copies=1, available_copies=1)
    book_id = get_book_by_isbn("1234567890124")["id"]
    borrow_date = datetime.now() - timedelta(days=1)
    due_date = borrow_date + timedelta(days=2)
    insert_borrow_record("123456", book_id, borrow_date, due_date)
    result = calculate_late_fee_for_book("123456", book_id)
    assert result["days_overdue"] == 0
    assert result["fee_amount"] == 0

def test_calculate_late_fee_for_book_overdue_7_days():
    """Test calculating late fee for book overdue by 7 days."""
    insert_book("Test Book", "Test Author", "1234567890124", total_copies=1, available_copies=1)
    book_id = get_book_by_isbn("1234567890124")["id"]
    borrow_date = datetime.now() - timedelta(days=8)
    due_date = borrow_date + timedelta(days=1)
    insert_borrow_record("123456", book_id, borrow_date, due_date)
    result = calculate_late_fee_for_book("123456", book_id)
    assert result["days_overdue"] == 7
    assert result["fee_amount"] == 3.5 # 7*0.5

def test_calculate_late_fee_for_book_overdue_14_days():
    """Test calculating late fee for book overdue by 14 days."""
    insert_book("Test Book", "Test Author", "1234567890124", total_copies=1, available_copies=1)
    book_id = get_book_by_isbn("1234567890124")["id"]
    borrow_date = datetime.now() - timedelta(days=15)
    due_date = borrow_date + timedelta(days=1)
    insert_borrow_record("123456", book_id, borrow_date, due_date)
    result = calculate_late_fee_for_book("123456", book_id)
    assert result["days_overdue"] == 14
    assert result["fee_amount"] == 10.5 # 7*0.5 + 7

def test_calculate_late_fee_for_book_overdue_21_days():
    """Test calculating late fee for book overdue by 21 days."""
    insert_book("Test Book", "Test Author", "1234567890124", total_copies=1, available_copies=1)
    book_id = get_book_by_isbn("1234567890124")["id"]
    borrow_date = datetime.now() - timedelta(days=22)
    due_date = borrow_date + timedelta(days=1)
    insert_borrow_record("123456", book_id, borrow_date, due_date)
    result = calculate_late_fee_for_book("123456", book_id)
    assert result["days_overdue"] == 21
    assert result["fee_amount"] == 15