import pytest
from unittest.mock import Mock
from services.library_service import pay_late_fees, refund_late_fee_payment
from services.payment_service import PaymentGateway
from database import reset_db

@pytest.fixture(scope="module", autouse=True)
def reset_database():
    """Reset database after all tests in this module run."""
    yield
    reset_db()

def test_pay_late_fees_successful_payment(mocker):
    mocker.patch('services.library_service.calculate_late_fee_for_book', return_value={'fee_amount': 10.50, 'days_overdue': 14, 'status': 'overdue'})
    mocker.patch('services.library_service.get_book_by_id', return_value={'id': 1, 'title': 'Test Book', 'author': 'Test Author'})
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (True, "txn_123456", "Payment processed successfully")
    success, message, transaction_id = pay_late_fees("123456", 1, mock_gateway)
    assert success == True
    assert "Payment successful" in message
    assert transaction_id == "txn_123456"
    mock_gateway.process_payment.assert_called_once_with(
        patron_id="123456",
        amount=10.50,
        description="Late fees for 'Test Book'"
    )
    
def test_pay_late_fees_payment_declined(mocker):
    mocker.patch('services.library_service.calculate_late_fee_for_book', return_value={'fee_amount': 10.50, 'days_overdue': 14, 'status': 'overdue'})
    mocker.patch('services.library_service.get_book_by_id', return_value={'id': 1, 'title': 'Test Book', 'author': 'Test Author'})
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (False, None, "Insufficient funds")
    success, message, transaction_id = pay_late_fees("123456", 2, mock_gateway)
    assert success == False
    assert "Payment failed" in message
    assert "Insufficient funds" in message
    assert transaction_id is None
    mock_gateway.process_payment.assert_called_once()

def test_pay_late_fees_invalid_patron_id(mocker):
    mock_gateway = Mock(spec=PaymentGateway)
    success, message, transaction_id = pay_late_fees("12345", 1, mock_gateway)
    assert success == False
    assert "Invalid patron ID" in message
    assert transaction_id is None
    mock_gateway.process_payment.assert_not_called()

def test_pay_late_fees_zero_late_fees(mocker):
    mocker.patch('services.library_service.calculate_late_fee_for_book', return_value={'fee_amount': 0.0, 'days_overdue': 0, 'status': 'not overdue'})
    mocker.patch('services.library_service.get_book_by_id', return_value={'id': 1, 'title': 'Test Book', 'author': 'Test Author'})
    mock_gateway = Mock(spec=PaymentGateway)
    success, message, transaction_id = pay_late_fees("123456", 1, mock_gateway)
    assert success == False
    assert "No late fees to pay" in message
    assert transaction_id is None
    mock_gateway.process_payment.assert_not_called()

def test_pay_late_fees_network_error_exception(mocker):
    mocker.patch('services.library_service.calculate_late_fee_for_book', return_value={'fee_amount': 10.50, 'days_overdue': 14, 'status': 'overdue'})
    mocker.patch('services.library_service.get_book_by_id', return_value={'id': 1, 'title': 'Test Book', 'author': 'Test Author'})
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.side_effect = Exception("Network timeout error")
    success, message, transaction_id = pay_late_fees("123456", 2, mock_gateway)
    assert success == False
    assert "Payment processing error" in message
    assert "Network timeout error" in message
    assert transaction_id is None
    mock_gateway.process_payment.assert_called_once()
    
def test_pay_late_fees_book_not_found(mocker):
    mocker.patch('services.library_service.calculate_late_fee_for_book', return_value={'fee_amount': 10.50, 'days_overdue': 14, 'status': 'overdue'})
    mocker.patch('services.library_service.get_book_by_id', return_value=None)
    mock_gateway = Mock(spec=PaymentGateway)
    success, message, transaction_id = pay_late_fees("123456", 2, mock_gateway)
    assert success == False
    assert "Book not found" in message
    assert transaction_id is None
    mock_gateway.process_payment.assert_not_called()

def test_pay_late_fees_empty_patron_id(mocker):
    mock_gateway = Mock(spec=PaymentGateway)
    success, message, transaction_id = pay_late_fees("", 1, mock_gateway)
    assert success == False
    assert "Invalid patron ID" in message
    mock_gateway.process_payment.assert_not_called()
    
def test_pay_late_fees_with_correct_amount(mocker):
    mocker.patch('services.library_service.calculate_late_fee_for_book', return_value={'fee_amount': 10.50, 'days_overdue': 14, 'status': 'overdue'})
    mocker.patch('services.library_service.get_book_by_id', return_value={'id': 2, 'title': 'Test Book', 'author': 'Test Author'})
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (True, "txn_max_fee", "Success")
    success, message, transaction_id = pay_late_fees("234567", 2, mock_gateway)
    mock_gateway.process_payment.assert_called_once_with(
        patron_id="234567",
        amount=10.50,
        description="Late fees for 'Test Book'"
    )

def test_refund_late_fee_payment_successful_refund(mocker):
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (True, "Refund of $10.50 processed successfully")
    success, message = refund_late_fee_payment("txn_123456", 10.50, mock_gateway)
    assert success == True
    assert "Refund of $10.50 processed successfully" in message
    mock_gateway.refund_payment.assert_called_once_with("txn_123456", 10.50)

def test_refund_late_fee_payment_invalid_transaction_id(mocker):
    mock_gateway = Mock(spec=PaymentGateway)
    success, message = refund_late_fee_payment("invalid_id", 10.50, mock_gateway)
    assert success == False
    assert "Invalid transaction ID" in message
    mock_gateway.refund_payment.assert_not_called()

def test_refund_late_fee_payment_invalid_refund_negative_amount(mocker):
    mock_gateway = Mock(spec=PaymentGateway)
    success, message = refund_late_fee_payment("txn_123456", -5.00, mock_gateway)
    assert success == False
    assert "must be greater than 0" in message
    mock_gateway.refund_payment.assert_not_called()

def test_refund_late_fee_payment_invalid_refund_zero_amount(mocker):
    mock_gateway = Mock(spec=PaymentGateway)
    success, message = refund_late_fee_payment("txn_123456", 0.0, mock_gateway)
    assert success == False
    assert "must be greater than 0" in message
    mock_gateway.refund_payment.assert_not_called()

def test_refund_late_fee_payment_invalid_refund_exceeds_max(mocker):
    mock_gateway = Mock(spec=PaymentGateway)
    success, message = refund_late_fee_payment("txn_123456", 20.00, mock_gateway)
    assert success == False
    assert "exceeds maximum late fee" in message
    mock_gateway.refund_payment.assert_not_called()
    
def test_refund_late_fee_payment_empty_transaction_id(mocker):
    mock_gateway = Mock(spec=PaymentGateway)
    success, message = refund_late_fee_payment("", 10.00, mock_gateway)
    assert success == False
    assert "Invalid transaction ID" in message
    mock_gateway.refund_payment.assert_not_called()