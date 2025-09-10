from datetime import datetime, timedelta
import pytest
from library_service import (
    calculate_late_fee_for_book, get_book_by_isbn
)
from database import (
    insert_borrow_record
)

def test_calculate_late_fee_for_book_not_overdue():
    """Test calculating late fee for book not overdue."""
    book_id = get_book_by_isbn("1234567890124")["id"]
    borrow_date = datetime.now() - timedelta(days=1)
    due_date = borrow_date + timedelta(days=2)
    insert_borrow_record("123456", book_id, borrow_date, due_date)
    result = calculate_late_fee_for_book("123456", book_id)
    assert result["days_overdue"] == 0
    assert result["fee_amount"] == 0

def test_calculate_late_fee_for_book_overdue_7_days():
    """Test calculating late fee for book overdue by 7 days."""
    book_id = get_book_by_isbn("1234567890124")["id"]
    borrow_date = datetime.now() - timedelta(days=8)
    due_date = borrow_date + timedelta(days=1)
    insert_borrow_record("123456", book_id, borrow_date, due_date)
    result = calculate_late_fee_for_book("123456", book_id)
    assert result["days_overdue"] == 7
    assert result["fee_amount"] == 3.5 # 7*0.5

def test_calculate_late_fee_for_book_overdue_14_days():
    """Test calculating late fee for book overdue by 14 days."""
    book_id = get_book_by_isbn("1234567890124")["id"]
    borrow_date = datetime.now() - timedelta(days=15)
    due_date = borrow_date + timedelta(days=1)
    insert_borrow_record("123456", book_id, borrow_date, due_date)
    result = calculate_late_fee_for_book("123456", book_id)
    assert result["days_overdue"] == 14
    assert result["fee_amount"] == 10.5 # 7*0.5 + 7

def test_calculate_late_fee_for_book_overdue_21_days():
    """Test calculating late fee for book overdue by 21 days."""
    book_id = get_book_by_isbn("1234567890124")["id"]
    borrow_date = datetime.now() - timedelta(days=22)
    due_date = borrow_date + timedelta(days=1)
    insert_borrow_record("123456", book_id, borrow_date, due_date)
    result = calculate_late_fee_for_book("123456", book_id)
    assert result["days_overdue"] == 21
    assert result["fee_amount"] == 15