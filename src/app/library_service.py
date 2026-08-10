"""Orchestration layer — coordinates domain models via a repository.

LibraryService holds business logic that spans multiple entities or requires
repository access. It depends only on the LibraryRepository protocol, never
on a concrete implementation (InMemory, SQL, etc.).
"""

from app.models import (
    BookID,
    BookNotLoanedError,
    Loan,
    LoanID,
    UserID,
)
from app.repository import LibraryRepository


class LibraryService:
    """Orchestrates library operations across domain models and persistence.

    The service is the single entry point for multi-entity workflows.
    It delegates validation to domain models and persistence to the
    repository, keeping both concerns separated.
    """

    def __init__(self, repository: LibraryRepository) -> None:
        """Initialize with any implementation of LibraryRepository."""
        self._repo = repository

    def loan_book(self, book_id: BookID, user_id: UserID) -> LoanID:
        """Loan a book to a user and return the new loan ID.

        Validates that both book and user exist, marks the book as loaned,
        and creates the loan in one step.

        Raises:
            BookNotFoundError: if the book ID does not exist.
            UserNotFoundError: if the user ID does not exist.
            BookAlreadyLoanedError: if the book is already loaned.
        """
        book = self._repo.get_book(book_id)
        self._repo.get_user(user_id)
        book.mark_as_loaned()
        return self._repo.add_loan(Loan(book_id, user_id))

    def return_book(self, book_id: BookID) -> None:
        """Return a loaned book, marking both book and loan as returned.

        Raises:
            BookNotFoundError: if the book ID does not exist.
            BookNotLoanedError: if the book has no active loan.
        """
        book = self._repo.get_book(book_id)
        loan = self._repo.get_active_loan_by_book(book_id)
        if loan is None:
            raise BookNotLoanedError(f"Book with id {book_id} is not currently loaned")
        book.mark_as_returned()
        loan.mark_as_returned()
