from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class User:
    """Represents a registered member of the library system."""

    username: str
    email: str
    id: int | None = None


@dataclass
class Book:
    """Represents a physical or digital book in the collection."""

    title: str
    author: str
    is_available: bool = True
    id: int | None = None


@dataclass
class Loan:
    """Represents the historical or active record of a book lent to a user."""

    user_id: int
    book_id: int
    loan_date: date
    return_date: Optional[date] = None
    id: int | None = None
