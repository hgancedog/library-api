from .models import Book, User, Loan, BookID, LoanID, UserID
from datetime import date


class InMemoryDatabase:

    def __init__(self):
        """Initializes data structures and auto-incrementing counters."""
        # Maps book_id (int) to its corresponding Book object
        self._books: dict[BookID, Book] = {}
        # Maps user_id (int) to its corresponding User object
        self._users: dict[UserID, User] = {}
        # Maps loan_id (int) to its corresponding Loan object
        self._loan_history: dict[LoanID, Loan] = {}
        # Maps book_id (int) -> Loan object (Optimized for availability checks)
        # CRITICAL: The key here is the book_id, NOT the loan_id.
        self._active_loans: dict[BookID, Loan] = {}

        self._next_book_id = 1
        self._next_user_id = 1
        self._next_loan_id = 1

    # --- PERSISTENCE ---
    def add_book(self, book: Book) -> None:
        """Implements book persistence with auto-incrementing ID."""
        book.id = self._next_book_id
        self._books[book.id] = book

        self._next_book_id += 1

    def add_user(self, user: User) -> None:
        """Implements user persistence with auto-incrementing ID."""
        user.id = self._next_user_id
        self._users[user.id] = user

        self._next_user_id += 1

    def save_loan(self, loan: Loan, book_id: BookID) -> None:
        """Persists loan data in history and active records."""
        loan.id = self._next_loan_id

        self._active_loans[book_id] = loan
        self._loan_history[loan.id] = loan

        self._next_loan_id += 1

    def remove_active_loan(self, book_id: BookID) -> bool:
        """Removes a loan record from the active tracking dictionary."""
        if book_id in self._active_loans:
            self._active_loans.pop(book_id, None)
            return True

        return False

    # --- QUERIES ---
    def get_book_by_id(self, book_id: BookID) -> Book | None:
        """Retrieves a book from the internal dictionary."""
        return self._books.get(book_id)

    def get_book_by_title(self, book_title: str) -> Book | None:
        """Performs a lookup in the internal dictionary to find a book by its title."""
        return next(
            (b for b in self._books.values() if b.title.lower() == book_title.lower()),
            None,
        )

    def get_user_by_id(self, user_id: UserID) -> User | None:
        """Retrieves a user from the internal dictionary."""
        return self._users.get(user_id)

    def get_active_loan(self, book_id: BookID) -> Loan | None:
        """Quick lookup for an active loan by book ID."""
        return self._active_loans.get(book_id)

    def get_all_books(self) -> list[Book]:
        """Returns a collection of all registered books."""
        return list(self._books.values())

    def get_all_users(self) -> list[User]:
        """Returns a collection of all registered members."""
        return list(self._users.values())

    def get_all_loans(self) -> list[Loan]:
        """Returns the full historical record of all loans."""
        return list(self._loan_history.values())

    def get_all_active_loans(self) -> list[Loan]:
        """Returns only the loans currently in progress."""
        return list(self._active_loans.values())

    # --- UPDATES ---
    def update_book_availability(self, book_id: BookID, is_available: bool) -> bool:
        """Directly modifies the availability attribute of a stored book."""
        book: Book | None = self.get_book_by_id(book_id)
        if book is not None:
            book.is_available = is_available
            return True
        return False

    def update_loan_status(self, book_id: BookID, return_date: date) -> bool:
        """Updates the return_date of an active loan record."""
        loan: Loan | None = self._active_loans.get(book_id)
        if loan is not None:
            loan.return_date = return_date
            return True
        return False


# Those lines ensure InMemoryDatabase correctly implements DbProtocol (Duck Typing validation)
from .protocols import DbProtocol

_: DbProtocol = InMemoryDatabase()
