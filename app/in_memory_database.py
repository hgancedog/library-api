from .models import Book, User, Loan
from datetime import date


class InMemoryDatabase:

    def __init__(self):
        """Initializes data structures and auto-incrementing counters."""
        # Maps book_id (int) to its corresponding Book object
        self.books: dict[int, Book] = {}
        # Maps user_id (int) to its corresponding User object
        self.users: dict[int, User] = {}
        # Maps loan_id (int) to its corresponding Loan object
        self.loan_history: dict[int, Loan] = {}
        # Stores active loans keyed by book_id for O(1) lookups
        self.active_loans: dict[int, Loan] = {}

        self._next_book_id = 1
        self._next_user_id = 1
        self._next_loan_id = 1

    # --- PERSISTENCE ---
    def add_book(self, book: Book) -> None:
        """Implements book persistence with auto-incrementing ID."""
        book.id = self._next_book_id
        self.books[book.id] = book

        self._next_book_id += 1

    def add_user(self, user: User) -> None:
        """Implements user persistence with auto-incrementing ID."""
        user.id = self._next_user_id
        self.users[user.id] = user

        self._next_user_id += 1

    def save_loan(self, loan: Loan, book_id: int) -> None:
        """Persists loan data in history and active records."""
        loan.id = self._next_loan_id

        self.active_loans[book_id] = loan
        self.loan_history[loan.id] = loan

        self._next_loan_id += 1

    def remove_active_loan(self, book_id: int) -> bool:
        """Removes a loan record from the active tracking dictionary."""
        if book_id in self.active_loans:
            self.active_loans.pop(book_id, None)
            return True

        return False

    # --- QUERIES ---
    def get_book_by_id(self, book_id: int) -> Book | None:
        """Retrieves a book from the internal dictionary."""
        return self.books.get(book_id)

    def get_user_by_id(self, user_id: int) -> User | None:
        """Retrieves a user from the internal dictionary."""
        return self.users.get(user_id)

    def get_active_loan(self, book_id: int) -> Loan | None:
        """Quick lookup for an active loan by book ID."""
        return self.active_loans.get(book_id)

    # --- UPDATES ---
    def update_book_availability(self, book_id: int, is_available: bool) -> bool:
        """Directly modifies the availability attribute of a stored book."""
        book: Book | None = self.get_book_by_id(book_id)
        if book:
            book.is_available = is_available
            return True
        return False

    def update_loan_status(self, book_id: int, return_date: date) -> bool:
        """Updates the return_date of an active loan record."""
        loan: Loan | None = self.active_loans.get(book_id)
        if loan:
            loan.return_date = return_date
            return True
        return False


# Those lines ensure InMemoryDatabase correctly implements DbProtocol (Duck Typing validation)
from .protocols import DbProtocol

_: DbProtocol = InMemoryDatabase()
