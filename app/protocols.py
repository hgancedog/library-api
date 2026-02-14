from datetime import date
from typing import Protocol

from .models import Book, BookID, Loan, User, UserID


class DbProtocol(Protocol):
    """Defines the interface for library database operations."""

    # --- COMMAND METHODS ---
    def add_book(self, book: Book):
        """Persists a new book record."""
        ...

    def add_user(self, user: User):
        """Persists a new user record."""
        ...

    def save_loan(self, loan: Loan, book_id: BookID):
        """Stores a new loan transaction associated with a book."""
        ...

    def remove_active_loan(self, book_id: BookID) -> bool:
        """Deletes a loan from active records. Returns True if successful."""
        ...

    # --- QUERY METHODS ---
    def get_book_by_id(self, book_id: BookID) -> Book | None:
        """Retrieves a book by its ID."""
        ...

    def get_book_by_title(self, book_title: str) -> Book | None:
        """Retrieves a book by its title."""
        ...

    def get_user_by_id(self, user_id: UserID) -> User | None:
        """Retrieves a user by their ID."""
        ...

    def get_active_loan(self, book_id: BookID) -> Loan | None:
        """Finds the current non-returned loan for a book."""
        ...

    def get_all_books(self) -> list[Book]:
        """Retrieves all books stored in the database repository."""
        ...

    def get_all_users(self) -> list[User]:
        """Retrieves all registered users from the database repository."""
        ...

    def get_all_loans(self) -> list[Loan]:
        """Retrieves the complete historical record of all loans."""
        ...

    def get_all_active_loans(self) -> list[Loan]:
        """Retrieves all currently active and non-returned loans."""
        ...

    # --- STATE MANAGEMENT METHODS ---
    def update_book_availability(self, book_id: BookID, is_available: bool) -> bool:
        """Updates the availability status of a book."""
        ...

    def update_loan_status(self, book_id: BookID, return_date: date) -> bool:
        """Updates a loan record with a return date."""
        ...
