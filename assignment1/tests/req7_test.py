import pytest
from library_service import (
    get_patron_status_report
)
from database import (
    reset_db
)

@pytest.fixture(scope="module", autouse=True)
def reset_database():
    """Reset database after all tests in this module run."""
    yield
    reset_db()

def test_get_patron_status_report_valid_input():
    """Test getting patron status report with valid input."""
    result = get_patron_status_report("123456")
    assert result == {}

def test_get_patron_status_report_invalid_patron_id_empty():
    """Test getting patron status report with empty patron id."""
    success, message = get_patron_status_report("")
    assert success == False
    assert "Invalid patron ID. Must be exactly 6 digits." in message

def test_get_patron_status_report_invalid_patron_id_too_long():
    """Test getting patron status report with patron id too long."""
    success, message = get_patron_status_report("1234567")
    assert success == False
    assert "Invalid patron ID. Must be exactly 6 digits." in message

def test_get_patron_status_report_invalid_patron_id_not_an_integer():
    """Test getting patron status report with patron id not an integer."""
    success, message = get_patron_status_report("a12345")
    assert success == False
    assert "Invalid patron ID. Must be exactly 6 digits." in message