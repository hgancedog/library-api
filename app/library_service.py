import re
from datetime import date
from .models import User, Book, Loan
from .protocols import DbProtocol
from app.exceptions import BookError, UserError, BookAlreadyLoanedError, LoanError


class LibraryService:

    # ! TODO - Documment methods

    def __init__(self, db: DbProtocol):
        self.db = db

    def register_book(self, book: Book) -> None:

        if not book.author or not book.author.strip():
            raise BookError(f"Book must have an autor")

        if not book.title or not book.title.strip():
            raise BookError("Book must have a title")

        self.db.add_book(book)

    def register_user(self, user: User) -> None:

        email_pattern = r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$"

        if not re.match(email_pattern, user.email.lower()):
            raise UserError(f"Invalid email format: {user.email}")

        if len(user.username) < 3 or not user.username.isalnum():
            raise UserError(f"Username must be alphanumeric and at least 3 characters")

        self.db.add_user(user)

    def check_book(self, book_id: int) -> bool:
        book = self.db.get_book_by_id(book_id)

        if not book:
            raise BookError(f"Book with ID {book_id} does not exists")

        if not book.is_available:
            raise BookAlreadyLoanedError(f"The book '{book.title}' is not available")

        loan = self.db.get_active_loan(book_id)

        if loan:
            user = self.db.get_user_by_id(loan.user_id)

            if user:
                username = user.username

                raise LoanError(
                    f"Book: {book.title} has been loaned by user {username}"
                )

            raise ValueError(
                f"Inconsistency: There is no user associated with the active loan of '{book.title}'"
            )

        return True

    def create_loan(self, user_id: int, book_id: int, loan_date: date) -> Loan | None:
        if not self.db.get_user_by_id(user_id):
            raise UserError(f"User with ID {user_id} does not exists")

        self.check_book(book_id)

        loan: Loan = Loan(user_id, book_id, loan_date)

        self.db.save_loan(loan, book_id)

        if not self.db.update_book_availability(book_id, False):
            raise BookError(f"Critical error: Could not reserve book {book_id}")

        return loan

    def mark_loan_as_returned(self, book_id: int, return_date: date) -> None:

        loan: Loan | None = self.db.get_active_loan(book_id)
        if not loan:
            raise LoanError(f"No active loan found for book Id {book_id}")

        if not self.db.update_loan_status(book_id, return_date):
            raise LoanError("Technical error: could not set return date")

        if not self.db.update_book_availability(book_id, True):
            raise BookError("Technical error: could not release book")

        if not self.db.remove_active_loan(book_id):
            raise LoanError("Technical error: could not remove loan from active list")
