import re
from datetime import date
from .models import User, Book, Loan, UserID, BookID
from .protocols import DbProtocol
from app.exceptions import (
    BookError,
    BookNotFoundError,
    UserError,
    BookAlreadyLoanedError,
    LoanError,
)


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

        Args:
            book: The Book object containing title and author data.

        Raises:
            BookError: If the book lacks a valid title or author.
        """

        if not book.author or not book.author.strip():
            raise BookError(f"Book must have an author")

        if not book.title or not book.title.strip():
            raise BookError("Book must have a title")

        self.db.add_book(book)

    def register_user(self, user: User) -> None:
        """
        Validates member data and registers them in the database.

        Args:
            user: The User object containing username and email.

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
    def check_book(self, book_id: BookID) -> bool:
        """
        Performs deep validation on a book's availability and loan status.

        Returns:
            bool: True if the book is ready for a new loan.

        Raises:
            BookNotFoundError: If no book matches the provided ID.
            BookAlreadyLoanedError: If the book is currently held by another user.
            UserError: If the user associated with an active loan cannot be found.
        """
        book = self.get_book_by_id(book_id)

        loan = self.db.get_active_loan(book_id)

        if loan:
            user = self.get_user_by_id(loan.user_id)
            username = user.username
            raise BookAlreadyLoanedError(
                f"Book: {book.title} has been loaned by user {username}"
            )

        return True

    def create_loan(
        self, user_id: UserID, book_id: BookID, loan_date: date
    ) -> Loan | None:
        """
        Executes the complete workflow to register a new book loan.

        This method validates both the borrower's existence and the book's
        availability before persisting the loan and updating the catalog.

        Args:
            user_id: The unique identifier of the borrower.
            book_id: The unique identifier of the book to be loaned.
            loan_date: The official start date of the loan.

        Returns:
            The created Loan object if the process completes successfully.

        Raises:
            UserError: If the borrower is not registered in the system.
            BookNotFoundError: If the requested book does not exist.
            BookAlreadyLoanedError: If the book is currently held by another user.
            BookError: If a critical failure occurs while updating book availability.
        """
        self.get_user_by_id(user_id)

        self.check_book(book_id)

        loan: Loan = Loan(user_id, book_id, loan_date)

        self.db.save_loan(loan, book_id)

        if not self.db.update_book_availability(book_id, False):
            raise BookError(f"Critical error: Could not reserve book {book_id}")

        return loan

    def mark_loan_as_returned(self, book_id: int, return_date: date) -> None:
        """
        Processes a return by closing the loan and releasing the book.

        Args:
            book_id: The unique identifier of the book being returned.
            return_date: The date when the book was physically returned.

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
    def get_book_by_id(self, book_id: BookID) -> Book:
        """
        Finds a specific book in the catalog by its unique ID.

        Args:
            book_id: The unique identifier of the book.

        Returns:
            The Book object associated with the given ID.

        Raises:
            BookNotFoundError: If no book is found with the specified ID.
        """
        book = self.db.get_book_by_id(book_id)
        if not book:
            raise BookNotFoundError(f"Book with ID {book_id} does not exist")

        return book

    def get_book_by_title(self, search_title: str) -> Book:
        """
        Search for a book in the catalog using its title.

        Args:
            search_title: The title of the book to find.

        Returns:
            The Book object if found.

        Raises:
            BookNotFoundError: If the title doesn't exist in the library.
        """
        book = self.db.get_book_by_title(search_title)

        if not book:
            raise BookNotFoundError(f"No book found with title: '{search_title}'")

        return book

    def get_user_by_id(self, user_id: UserID) -> User:
        """
        Retrieves a registered user from the system.

        Args:
            user_id: The unique identifier of the user to retrieve.

        Returns:
            The User object if the lookup is successful.

        Raises:
            UserError: If no user matches the provided ID, preventing
                   invalid loan operations.
        """
        user = self.db.get_user_by_id(user_id)

        if not user:
            raise UserError(f"User with ID {user_id} does not exist")

        return user

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
