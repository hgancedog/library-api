from .models import Book, User, Loan
from datetime import date


class InMemoryDatabase:

    def __init__(self):
        # Maps book_id (int) to its corresponding Book object
        self.books: dict[int, Book] = {}

        # Maps user_id (int) to its corresponding User object
        self.users: dict[int, User] = {}

        # Maps loan_id (int) to its corresponding Loan object
        self.loan_history: dict[int, Loan] = {}

        # NOTE: For this MVP, we use book_id as the key for active loans.
        # This assumes a 1-to-1 relationship (one physical copy per book).
        # It allows for O(1) performance during the return process.
        self.active_loans: dict[int, Loan] = {}

    # --- COMMAND METHODS ---
    def add_book(self, book: Book) -> None:
        self.books[book.id] = book

    def add_user(self, user: User) -> None:
        self.users[user.id] = user

    def save_loan(self, loan: Loan, book_id: int) -> None:
        self.active_loans[book_id] = loan
        self.loan_history[loan.id] = loan

    def remove_active_loan(self, book_id: int) -> None:
        if book_id in self.active_loans:
            self.active_loans.pop(book_id, None)

    # --- QUERY METHODS ---
    def get_book_by_id(self, book_id: int) -> Book | None:
        return self.books.get(book_id)

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.users.get(user_id)

    def get_active_loan(self, book_id: int) -> Loan | None:
        return self.active_loans.get(book_id)

    # --- STATE MANAGEMENT METHODS ---
    def update_book_availability(self, book_id: int, is_available: bool) -> None:
        book = self.get_book_by_id(book_id)
        if book:
            book.is_available = is_available

    def update_loan_status(self, book_id: int) -> None:
        loan = self.active_loans.get(book_id)
        if loan:
            loan.return_date = date.today()


# Those lines ensure InMemoryDatabase correctly implements DbProtocol (Duck Typing validation)
from .protocols import DbProtocol

_: DbProtocol = InMemoryDatabase()
