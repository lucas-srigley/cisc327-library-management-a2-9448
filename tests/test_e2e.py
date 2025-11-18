import pytest
import subprocess
import time
import os
import signal
from playwright.sync_api import Page, expect
from database import reset_db

BASE_URL = "http://localhost:5000"
flask_process = None

@pytest.fixture(scope="session", autouse=True)
def start_flask_app():
    global flask_process
    
    reset_db()
    
    flask_process = subprocess.Popen(
        ["python", "app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid if os.name != 'nt' else None
    )
    
    time.sleep(3)
    
    yield
    
    if flask_process:
        try:
            if os.name == 'nt':
                flask_process.terminate()
            else:
                os.killpg(os.getpgid(flask_process.pid), signal.SIGTERM)
            flask_process.wait()
        except ProcessLookupError:
            pass
    
    reset_db()

@pytest.fixture(scope="function")
def page(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()
    browser.close()


def test_add_book_and_verify_in_catalog(page: Page):
    page.goto(f"{BASE_URL}/add_book")
    expect(page).to_have_title("Library Management System")
    expect(page.locator("h2")).to_contain_text("Add New Book")
    
    test_isbn = "9781234567890"
    test_title = "E2E Test Book"
    test_author = "Test Author"
    test_copies = "5"
    
    page.fill("#title", test_title)
    page.fill("#author", test_author)
    page.fill("#isbn", test_isbn)
    page.fill("#total_copies", test_copies)
    
    page.click("button[type='submit']")
    
    expect(page.locator(".flash-success")).to_be_visible()
    expect(page.locator(".flash-success")).to_contain_text("successfully added")
    
    expect(page).to_have_url(f"{BASE_URL}/catalog")
        
    book_row = page.locator(f"tr:has-text('{test_title}')")
    expect(book_row).to_be_visible()
    
    expect(book_row).to_contain_text(test_title)
    expect(book_row).to_contain_text(test_author)
    expect(book_row).to_contain_text(test_isbn)
    expect(book_row).to_contain_text(f"{test_copies}/{test_copies} Available")


def test_borrow_book_flow(page: Page):
    page.goto(f"{BASE_URL}/catalog")
    expect(page.locator("h2")).to_contain_text("Book Catalog")
    
    available_book_row = page.locator("tr:has-text('The Great Gatsby')").first
    expect(available_book_row).to_be_visible()
    
    availability_text = available_book_row.locator(".status-available").inner_text()
    initial_available = int(availability_text.split("/")[0])
    
    patron_id = "123456"
    patron_input = available_book_row.locator("input[name='patron_id']")
    patron_input.fill(patron_id)
    
    borrow_button = available_book_row.locator("button:has-text('Borrow')")
    borrow_button.click()
    
    expect(page.locator(".flash-success")).to_be_visible()
    expect(page.locator(".flash-success")).to_contain_text("Successfully borrowed")
    expect(page.locator(".flash-success")).to_contain_text("Due date")
    
    updated_book_row = page.locator("tr:has-text('The Great Gatsby')").first
    updated_availability_text = updated_book_row.locator(".status-available").inner_text()
    updated_available = int(updated_availability_text.split("/")[0])
    
    assert updated_available == initial_available - 1, "Available copies should decrease by 1"


def test_search_book_functionality(page: Page):
    page.goto(f"{BASE_URL}/search")
    expect(page.locator("h2")).to_contain_text("Search Books")
    
    search_term = "1984"
    page.fill("#q", search_term)
    
    page.select_option("#type", "title")
    
    page.click("button:has-text('Search')")
    
    expect(page.locator("h3")).to_contain_text(f'Search Results for "{search_term}"')
    
    results_table = page.locator("table")
    expect(results_table).to_be_visible()
    expect(results_table).to_contain_text("1984")
    expect(results_table).to_contain_text("George Orwell")


def test_return_book_flow(page: Page):
    page.goto(f"{BASE_URL}/catalog")
    
    book_id = None
    mockingbird_row = page.locator("tr:has-text('To Kill a Mockingbird')").first
    if mockingbird_row.locator("input[name='patron_id']").is_visible():
        mockingbird_row.locator("input[name='patron_id']").fill("123456")
        mockingbird_row.locator("button:has-text('Borrow')").click()
        book_id = mockingbird_row.locator("input[name='book_id']").input_value()
        time.sleep(1)
    
    page.goto(f"{BASE_URL}/return")
    expect(page.locator("h2")).to_contain_text("Return Book")
    
    page.fill("#patron_id", "123456")
    page.fill("#book_id", book_id)
    
    page.click("button:has-text('Process Return')")
    
    flash_message = page.locator(".flash-success, .flash-error")
    expect(flash_message).to_be_visible()
    expect(flash_message).to_contain_text("Successfully returned")


def test_patron_status_flow(page: Page):
    page.goto(f"{BASE_URL}/patron_status")
    expect(page.locator("h2")).to_contain_text("Patron Status")
    
    patron_id = "123456"
    page.fill("input[name='patron_id']", patron_id)
    
    page.click("button:has-text('Check Status')")
    
    expect(page.locator("h3")).to_contain_text(f"Patron ID: {patron_id}")
    
    expect(page.locator("p:has-text('Total books currently borrowed')")).to_be_visible()
    expect(page.locator("p:has-text('Borrowing limit remaining')")).to_be_visible()
    expect(page.locator("p:has-text('Total late fees owed')")).to_be_visible()


def test_invalid_isbn_validation(page: Page):
    page.goto(f"{BASE_URL}/add_book")
    
    page.fill("#title", "Invalid ISBN Book")
    page.fill("#author", "Test Author")
    page.fill("#isbn", "123")
    page.fill("#total_copies", "3")
    
    page.click("button[type='submit']")
    
    expect(page.locator(".flash-error")).to_be_visible()
    expect(page.locator(".flash-error")).to_contain_text("13 digits")


def test_navigation_links(page: Page):
    page.goto(f"{BASE_URL}/catalog")
    
    page.click("a:has-text('Add Book')")
    expect(page).to_have_url(f"{BASE_URL}/add_book")
    expect(page.locator("h2")).to_contain_text("Add New Book")
    
    page.click("a:has-text('Return Book')")
    expect(page).to_have_url(f"{BASE_URL}/return")
    expect(page.locator("h2")).to_contain_text("Return Book")
    
    page.click("a:has-text('Search')")
    expect(page).to_have_url(f"{BASE_URL}/search")
    expect(page.locator("h2")).to_contain_text("Search Books")
    
    page.click("a:has-text('Catalog')")
    expect(page).to_have_url(f"{BASE_URL}/catalog")
    expect(page.locator("h2")).to_contain_text("Book Catalog")
    
    page.click("a:has-text('Patron Status')")
    expect(page).to_have_url(f"{BASE_URL}/patron_status")
    expect(page.locator("h2")).to_contain_text("Patron Status")