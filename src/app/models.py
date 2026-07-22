import re
from dataclasses import dataclass, field
from datetime import date, timedelta

BookID = int
UserID = int
LoanID = int


class LibraryApiError(Exception):
    """Base exception for all library API errors."""


class BookError(LibraryApiError):
    """Raised for general book-related failures."""


class BookAlreadyLoanedError(BookError):
    """Raised when attempting to loan a book that is already out."""


class BookNotLoanedError(BookError):
    """Raised when attempting to return a book that is not loaned."""


class BookNotFoundError(BookError):
    """Raised when a book ID does not exist in the repository."""


class UserError(LibraryApiError):
    """Raised for general user-related failures."""


class LoanError(LibraryApiError):
    """Raised for general loan-related failures."""


_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if not _EMAIL_RE.match(self.value):
            raise ValueError("Invalid email format")
        object.__setattr__(self, "value", self.value.lower())


@dataclass
class Book:
    title: str
    author: str
    is_available: bool = True
    book_id: BookID | None = None

    def __post_init__(self):
        if not self.title or not self.title.strip():
            raise BookError("Book must have a title")
        if not self.author or not self.author.strip():
            raise BookError("Book must have an author")

    def can_be_loaned(self) -> bool:
        return self.is_available

    def mark_as_loaned(self):
        if not self.is_available:
            raise BookAlreadyLoanedError(f"Book '{self.title}' is already loaned")
        self.is_available = False

    def mark_as_returned(self):
        if self.is_available:
            raise BookNotLoanedError(f"Book '{self.title}' is not currently loaned")
        self.is_available = True


@dataclass
class User:
    username: str
    email: Email
    user_id: UserID | None = None

    def __post_init__(self):
        if not self.username or not self.username.strip():
            raise UserError("User must have an username")


@dataclass
class Loan:
    book_id: BookID
    user_id: UserID
    loan_date: date = field(default_factory=date.today)
    return_date: date | None = None
    loan_id: LoanID | None = None

    def __post_init__(self):
        if self.return_date is not None and self.return_date < self.loan_date:
            raise LoanError("return_date cannot be earlier than loan_date")

    def is_active(self) -> bool:
        return self.return_date is None

    def mark_as_returned(self, return_date: date | None = None):
        self.return_date = return_date if return_date is not None else date.today()

    @property
    def due_date(self) -> date:
        return self.loan_date + timedelta(30)
