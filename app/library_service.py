import re
from datetime import date
from .models import User, Book, Loan, UserID, BookID
from .protocols import DbProtocol
from app.exceptions import BookError, UserError, BookAlreadyLoanedError, LoanError


class LibraryService:
    """
    Orchestrates library business logic by connecting models with
    the database persistence layer.
    """

    def __init__(self, db: DbProtocol):
        """Initializes the service with a specific database implementation."""
        self.db = db

    # --- REGISTRATION ---
    def register_book(self, book: Book) -> None:
        """
        Validates and adds a new book to the system.

        Raises:
            BookError: If the book lacks a valid title or author.
        """

        if not book.author or not book.author.strip():
            raise BookError(f"Book must have an autor")

        if not book.title or not book.title.strip():
            raise BookError("Book must have a title")

        self.db.add_book(book)

    def register_user(self, user: User) -> None:
        """
        Validates member data and registers them in the database.

        Raises:
            UserError: If the email format is invalid or username is too short.
        """

        email_pattern = r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$"

        if not re.match(email_pattern, user.email.lower()):
            raise UserError(f"Invalid email format: {user.email}")

        if len(user.username) < 3 or not user.username.isalnum():
            raise UserError(f"Username must be alphanumeric and at least 3 characters")

        self.db.add_user(user)

    # --- BUSINESS LOGIC ---
    def check_book(self, book_id: int) -> bool:
        """
        Performs deep validation on a book's availability and loan status.

        Returns:
            bool: True if the book is ready for a new loan.

        Raises:
            BookError: If the book doesn't exist.
            BookAlreadyLoanedError: If the book is marked as unavailable.
            LoanError: If there's a conflict with active loans.
            ValueError: If data inconsistency is detected between book and user.
        """
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

    def create_loan(
        self, user_id: UserID, book_id: BookID, loan_date: date
    ) -> Loan | None:
        """
        High-level process to create a loan, including all safety checks.

        Raises:
            UserError: If the user ID is not registered.
            BookError: If the book cannot be reserved in the database.
        """
        if not self.db.get_user_by_id(user_id):
            raise UserError(f"User with ID {user_id} does not exists")

        self.check_book(book_id)

        loan: Loan = Loan(user_id, book_id, loan_date)

        self.db.save_loan(loan, book_id)

        if not self.db.update_book_availability(book_id, False):
            raise BookError(f"Critical error: Could not reserve book {book_id}")

        return loan

    def mark_loan_as_returned(self, book_id: int, return_date: date) -> None:
        """
        Processes a return by closing the loan and releasing the book.

        Raises:
            LoanError: If no active loan is found for the book.
            BookError: If there's a technical failure updating the database.
        """

        loan: Loan | None = self.db.get_active_loan(book_id)
        if not loan:
            raise LoanError(f"No active loan found for book Id {book_id}")

        if not self.db.update_loan_status(book_id, return_date):
            raise LoanError("Technical error: could not set return date")

        if not self.db.update_book_availability(book_id, True):
            raise BookError("Technical error: could not release book")

        if not self.db.remove_active_loan(book_id):
            raise LoanError("Technical error: could not remove loan from active list")

    # --- QUERY OPERATIONS ---
    def get_all_books(self) -> list[Book]:
        """Retrieves the complete list of books available in the system."""
        return self.db.get_all_books()

    def get_all_users(self) -> list[User]:
        """Retrieves all registered library members."""
        return self.db.get_all_users()

    def get_all_loans(self) -> list[Loan]:
        """Retrieves the entire history of book loans."""
        return self.db.get_all_loans()

    def get_active_loans(self) -> list[Loan]:
        """Provides a real-time list of books that are currently out on loan."""
        return self.db.get_all_active_loans()
