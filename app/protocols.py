from datetime import date
from typing import Protocol
from .models import Book, User, Loan


class DbProtocol(Protocol):
    """Defines the interface for library database operations."""

    # --- COMMAND METHODS ---
    def add_book(self, book: Book):
        """Persists a new book record."""
        ...

    def add_user(self, user: User):
        """Persists a new user record."""
        ...

    def save_loan(self, loan: Loan, book_id: int):
        """Stores a new loan transaction associated with a book."""
        ...

    def remove_active_loan(self, book_id: int) -> bool:
        """Deletes a loan from active records. Returns True if successful."""
        ...

    # --- QUERY METHODS ---
    def get_book_by_id(self, book_id: int) -> Book | None:
        """Retrieves a book by its ID. Returns None if not found."""
        ...

    def get_user_by_id(self, user_id: int) -> User | None:
        """Retrieves a user by their ID. Returns None if not found."""
        ...

    def get_active_loan(self, book_id: int) -> Loan | None:
        """Finds the current non-returned loan for a book."""
        ...

    # --- STATE MANAGEMENT METHODS ---
    def update_book_availability(self, book_id: int, is_available: bool) -> bool:
        """Updates the availability status of a book."""
        ...

    def update_loan_status(self, book_id: int, return_date: date) -> bool:
        """Updates a loan record with a return date."""
        ...
