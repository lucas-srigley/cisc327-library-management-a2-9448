import pytest
from library_service import (
    add_book_to_catalog
)

def test_add_book_valid_input():
    """Test adding a book with valid input."""
    success, message = add_book_to_catalog("Req 1 Test Book", "Test Author", "1234567890124", 5)
    assert success == True
    assert "successfully added" in message.lower()
    
# title tests
def test_add_book_invalid_title_empty():
    """Test adding a book with an empty title."""
    success, message = add_book_to_catalog("", "Test Author", "1234567890123", 5)
    assert success == False
    assert "Title is required." in message
    
def test_add_book_invalid_title_too_long():
    """Test adding a book with title too long (> 200 characters)."""
    title_too_long = "T" * 201
    success, message = add_book_to_catalog(title_too_long, "Test Author", "1234567890123", 5)
    assert success == False
    assert "Title must be less than 200 characters." in message

# author tests
def test_add_book_invalid_author_empty():
    """Test adding a book with an empty author."""
    success, message = add_book_to_catalog("Test Title", "", "1234567890123", 5)
    assert success == False
    assert "Author is required." in message
    
def test_add_book_invalid_title_too_long():
    """Test adding a book with author too long (> 100 characters)."""
    author_too_long = "T" * 101
    success, message = add_book_to_catalog("Test Title", author_too_long, "1234567890123", 5)
    assert success == False
    assert "Author must be less than 100 characters." in message

# isbn tests
def test_add_book_invalid_isbn_too_short():
    """Test adding a book with ISBN too short."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "123456789", 5)
    assert success == False
    assert "ISBN must be exactly 13 digits." in message

def test_add_book_invalid_isbn_too_long():
    """Test adding a book with ISBN too long."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "12345678901230", 5)
    assert success == False
    assert "ISBN must be exactly 13 digits." in message
    
def test_add_book_invalid_isbn_already_exists():
    """Test adding a book with ISBN that already exists."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5)
    assert success == False
    assert "A book with this ISBN already exists." in message
    
# total copies tests
def test_add_book_invalid_total_copies_zero():
    """Test adding a book with total copies = 0."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 0)
    assert success == False
    assert "Total copies must be a positive integer." in message

def test_add_book_invalid_total_copies_not_a_number():
    """Test adding a book with ISBN too long."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 'T')
    assert success == False
    assert "Total copies must be a positive integer." in message

def test_add_book_invalid_total_copies_negative():
    """Test adding a book with ISBN too long."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", -1)
    assert success == False
    assert "Total copies must be a positive integer." in message