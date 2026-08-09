from typing import Protocol

from app.models import (
    Book,
    BookID,
    BookNotFoundError,
    BookNotLoanedError,
    Loan,
    LoanID,
    LoanNotFoundError,
    User,
    UserID,
    UserNotFoundError,
)


class LibraryRepository(Protocol):
    """Structural interface for library persistence.

    Any implementation (in-memory, SQL, etc.) must satisfy this protocol.
    Swappable without modifying tests or domain code.
    """

    def add_book(self, book: Book) -> BookID:
        """Add a book and return its new ID."""
        ...

    def get_book(self, book_id: BookID) -> Book:
        """Retrieve a book by ID. Raises BookNotFoundError."""
        ...

    def get_all_books(self) -> dict[BookID, Book]:
        """Return a copy of all stored books."""
        ...

    def return_book(self, book_id: BookID) -> None:
        """Return a loaned book. Raises BookNotLoanedError."""
        ...

    def loan_book(self, book_id: BookID, user_id: UserID) -> LoanID:
        """Loan a book to a user and return the new loan ID."""
        ...

    def add_user(self, user: User) -> UserID:
        """Add a user and return their new ID."""
        ...

    def get_user(self, user_id: UserID) -> User:
        """Retrieve a user by ID. Raises UserNotFoundError."""
        ...

    def add_loan(self, loan: Loan) -> LoanID:
        """Store a loan and return its new ID.

        Prefer loan_book() for the full loan workflow with validation.
        """
        ...

    def get_loan(self, loan_id: LoanID) -> Loan:
        """Retrieve a loan by ID. Raises LoanNotFoundError."""
        ...

    def get_active_loans_by_user(self, user_id: UserID) -> list[Loan]:
        """Return all active loans for a given user."""
        ...

    def get_active_loan_by_book(self, book_id: BookID) -> Loan | None:
        """Return the active loan for a book, or None."""
        ...


class InMemoryRepository:
    """Dictionary-backed implementation of LibraryRepository.

    Stores books, users, and loans in plain dicts with auto-incrementing
    integer IDs. Suitable for Stage 1 — no persistence, no database.
    """

    def __init__(self):
        """Initialize empty storage dicts and ID counters."""
        self._db_books: dict[BookID, Book] = {}
        self._db_users: dict[UserID, User] = {}
        self._db_loans: dict[LoanID, Loan] = {}
        self._next_book_id: BookID = 1
        self._next_user_id: UserID = 1
        self._next_loan_id: LoanID = 1

    def add_book(self, book: Book) -> BookID:
        """Assign an auto-incremented ID and store the book."""
        book.book_id = self._next_book_id
        self._db_books[book.book_id] = book
        self._next_book_id += 1
        return book.book_id

    def get_book(self, book_id: BookID) -> Book:
        """Retrieve a book by ID.

        Raises BookNotFoundError if the ID does not exist.
        """
        if book_id not in self._db_books:
            raise BookNotFoundError(f"Book with id {book_id} not found")
        return self._db_books[book_id]

    def get_all_books(self) -> dict[BookID, Book]:
        """Return a shallow copy of the full book catalog."""
        return dict(self._db_books)

    def return_book(self, book_id: BookID) -> None:
        """Return a loaned book, marking both book and loan as returned.

        Raises BookNotFoundError if the book ID does not exist.
        Raises BookNotLoanedError if the book has no active loan.
        """
        book = self.get_book(book_id)
        loan = self.get_active_loan_by_book(book_id)
        if loan is None:
            raise BookNotLoanedError(f"Book with id {book_id} is not currently loaned")
        book.mark_as_returned()
        loan.mark_as_returned()

    def loan_book(self, book_id: BookID, user_id: UserID) -> LoanID:
        """Loan a book to a user and return the new loan ID.

        Validates that both book and user exist, then marks the book as
        loaned and creates the loan in one step.

        Raises BookNotFoundError if the book ID does not exist.
        Raises UserNotFoundError if the user ID does not exist.
        Raises BookAlreadyLoanedError if the book is already loaned.
        """
        book = self.get_book(book_id)
        self.get_user(user_id)
        book.mark_as_loaned()
        return self.add_loan(Loan(book_id, user_id))

    def add_user(self, user: User) -> UserID:
        """Assign an auto-incremented ID and store the user."""
        user.user_id = self._next_user_id
        self._db_users[user.user_id] = user
        self._next_user_id += 1
        return user.user_id

    def get_user(self, user_id: UserID) -> User:
        """Retrieve a user by ID.

        Raises UserNotFoundError if the ID does not exist.
        """
        if user_id not in self._db_users:
            raise UserNotFoundError(f"User with id {user_id} not found")
        return self._db_users[user_id]

    def add_loan(self, loan: Loan) -> LoanID:
        """Assign an auto-incremented ID and store the loan.

        Prefer loan_book() for the full loan workflow with validation.
        """
        loan.loan_id = self._next_loan_id
        self._db_loans[loan.loan_id] = loan
        self._next_loan_id += 1
        return loan.loan_id

    def get_loan(self, loan_id: LoanID) -> Loan:
        """Retrieve a loan by ID.

        Raises LoanNotFoundError if the ID does not exist.
        """
        if loan_id not in self._db_loans:
            raise LoanNotFoundError(f"Loan with id {loan_id} not found")
        return self._db_loans[loan_id]

    def get_active_loans_by_user(self, user_id: UserID) -> list[Loan]:
        """Return all active (non-returned) loans for a given user."""
        loans: list[Loan] = []

        for loan in self._db_loans.values():
            if user_id == loan.user_id and loan.is_active():
                loans.append(loan)

        return loans

    def get_active_loan_by_book(self, book_id: BookID) -> Loan | None:
        """Return the active loan for a book, or None if not loaned."""
        for loan in self._db_loans.values():
            if loan.book_id == book_id and loan.is_active():
                return loan
        return None


_: LibraryRepository = InMemoryRepository()
